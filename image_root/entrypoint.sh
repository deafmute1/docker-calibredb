#!/bin/bash  

### FUNCTIONS 
# run's user modification command
# $1 = file (with path), $2 = parent folder
function modifier () {
    set -x 
    eval "$importDictDefinition" 
    if [[ ${importDict[$2]} == "" ]]; then # "" = no command 
        return 0
    fi
    prevFileCount=$(find "/calibre/import/${folder}" -type f -printf '.' | wc -c)
    ${importDict[$2]} "$1"
    # check if command created a new file, delete original if so 
    if [[ $(find "/calibre/import/${folder}" -type f -printf '.' | wc -c) -gt $prevFileCount ]]; then  
        rm "$1"
    fi
    return 0
}

### SETUP
# setup log
exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3
exec 1>/calibre/config/entrypoint.log 2>&1

# setup environment
set -x # verbose trace output, probably don't need this in final
umask "$UMASK_SET"
su - root # make sure we're root, this should happen anyway
export -f modifier # add functions to env for find -exec, bash -c etc.

# setup defaults if necessary, should only happen on first run
if [[ ! -f /calibre/config/imports ]]; then   
    cp /calibre/defaults/imports /calibre/config/imports
fi

if [[ ! -f /calibre/library/metadata.db ]]; then   
    cp /calibre/defaults/metadata.db /calibre/library/metadata.db
fi

# generate import rules
if [[ -f /calibre/config/imports ]];  then
    declare -A importDict
    while read -r folder args; do
        importDict["$folder"]="$args"
        # create folder if it doesn't exist
        if [[ ! -d "/calibre/import/${folder}" ]]; then
            mkdir -p "/calibre/import/${folder}"
        fi
    done < "/calibre/config/imports"
    importDictDefinition="$(declare -p importDict)" # allow export of array to child shell using its definition and eval
    export importDictDefinition
fi

# run additional setup scripts
for script in /calibre/config/bash.setup.d/*; do
    bash "$script" -H || break
done

### MAIN 
while true; do
    for folder in "${!importDict[@]}"; do
        # use workingDir to prevent issues arising from writes to $folder between/during steps 
        workingDir=/tmp/calibre_import-$RANDOM
        mkdir "$workingDir"
        cp -r /calibre/import/"$folder"/* "$workingDir"
        find "$workingDir" -type f -exec bash -c 'modifier "$1" "$2"' _ {} "$folder" \; 
        find "$workingDir" -type f -exec sh -c 'calibredb add --with-library /calibre/library "$1"; -exec rm -r "$1"' _ {} \;
        rm -r  "$workingDir"
        if [[ $DELETE_IMPORTED == true ]]; then
            rm -r /calibre/import/"$folder"/*
        fi
    done 
    for script in /calibre/config/bash.timer.d/*; do
        bash "$script" -H || break
    done
    chown -R "$LIBRARY_UID":"$LIBRARY_GID" /calibre/library
    sleep "$IMPORT_TIME"
done