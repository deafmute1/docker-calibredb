#!/bin/bash  

### FUNCTIONS 
# run's user modification command
# $1 = file (with path), $2 = parent folder
function modifier () {
    if [[ ${importDict[$2]} == "" ]]; then # "" denotes no command to apply
        return 0
    fi
    prevFileCount=$(find "/calibre/import/${folder}" -type f -printf '.' | wc -c)
    ${importDict[$2]} "$1"
    # check if command created a new file, delete if so 
    if [[ $(find "/calibre/import/${folder}" -type f -printf '.' | wc -c) -gt $prevFileCount ]]; then  
        rm "$1"
    fi
    return 0
}


### SETUP
umask "$UMASK_SET"

#create logs and ln to stdout for docker log command
if [[ ! -d /var/log/calibre ]]; then
    mkdir -p /var/log/calibre 
fi
exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3
exec 1>/var/log/calibre/entrypoint.log 2>&1
ln -s /var/log/calibre/entrypoint.log /dev/stdout

# setup defaults if necessary, should only happen on first run
if [[ ! -f /calibre/config/import.config ]]; then   
    cp /calibre/defaults/import.config /calibre/config/import.config
fi

if [[ ! -f /calibre/library/metadata.db ]]; then   
    cp /calibre/defaults/metadata.db /calibre/library/metadata.db
fi

if [[ ! -d /calibre/config/bash.d ]]; then
    mkdir -p /calibre/config/bash.d
fi

# generate import rules
if [[ -f /calibre/config/import.config ]]; then
    declare -A importDict
    while read -r folder args; do
        importDict["$folder"]="$args"
        # create folder if it doesn't exist
        if [[ ! -d "/calibre/import/${folder}" ]]; then
            mkdir -p "/calibre/import/${folder}"
        fi
    done < /calibre/config/import.config
fi

### MAIN 
while true; do
    for folder in "${!importDict[@]}"; do
        find "/calibre/import/${folder}/" -type f -exec sh -c 'modifier "$1" "$folder"' _ {} \; 
        find "/calibre/import/${folder}" -type f -exec sh -c 'calibredb add --with-library /calibre/library "$1"; -exec rm -r "$1"' _ {} \;
    done 
    for script in /calibre/config/bash.d/*; do
        bash "$script" -H || break
    done
    sleep "$IMPORT_TIME"
done

        





