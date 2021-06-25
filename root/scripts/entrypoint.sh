#!/bin/bash  

### FUNCTIONS 
# run's user modification command
# $1 = file (with path), $2 = parent folder
function modifier () {
    eval "$importDictDefinition" 
    # "" = no command 
    [[ ${importDict[$2]} == "" ]] && return 0
    prevFileCount=$(find "/calibre/import/${folder}" -type f -printf '.' | wc -c)
    # run modification
    ${importDict[$2]} "$1"
    # check if command created a new file, delete original if so 
    [[ $(find "/calibre/import/${folder}" -type f -printf '.' | wc -c) -gt $prevFileCount ]] && rm "$1"
    return 0
}

### SETUP
# setup log
exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3
exec 1>/calibre/config/entrypoint.log 2>&1
[[ "$VERBOSE" == true ]] && set -x

# setup environment
umask "$UMASK_SET"
export -f modifier # add functions to env

# setup defaults if necessary, should only happen on first run
[[ ! -f /calibre/config/imports ]] && cp /calibre/defaults/imports /calibre/config/imports
[[ ! -f /calibre/library/metadata.db ]] && cp /calibre/defaults/metadata.db /calibre/library/metadata.db

# generate import rules
if [[ -f /calibre/config/imports ]];  then
    declare -A importDict
    while read -r folder args; do
        importDict["$folder"]="$args"
        # create folder if it doesn't exist
        [[ ! -d "/calibre/import/${folder}" ]] && mkdir -p "/calibre/import/${folder}"
    done < "/calibre/config/imports"
    # allow export of array to child shell using its definition and eval
    importDictDefinition="$(declare -p importDict)" 
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
        # use find to run modifications, then import on each file below $folder
        # note that find -exec creates a subshell; set -x also does not apply to subshells.
        find "$workingDir" -type f -exec bash -c '[[ "$VERBOSE" == true ]] && set -x; modifier "$1" "$2"' _ {} "$folder" \; 
        find "$workingDir" -type f -exec bash -c '[[ "$VERBOSE" == true ]] && set -x; calibredb add --with-library /calibre/library "$1"' _ {} \;
        # clean up
        rm -r  "$workingDir"
        [[ $DELETE_IMPORTED == true ]] && rm -r /calibre/import/"$folder"/*
    done 
    for script in /calibre/config/bash.timer.d/*; do
        bash "$script" -H || break
    done
    chown -R "$LIBRARY_UID":"$LIBRARY_GID" /calibre/library
    sleep "$IMPORT_TIME"
done
