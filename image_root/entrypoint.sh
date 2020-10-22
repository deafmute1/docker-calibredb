#!/bin/bash  

#create logs
exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3
exec 1>/calibre/config/calibre-$(date +%Y%m%d-%H%M%S).log 2>&1

umask $UMASK_SET

# import defaults if necessary
if [[ ! -f /calibre/config/import.config]]; then   
    cp /calibre/defaults/import.config /calibre/config/import.config
fi

if [[ ! -f /calibre/library/metadata.db]]; then   
    cp /calibre/defaults/metadata.db/calibre/library/metadata.db
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

# run's user modification command
# $1 = file (with path), $2 = parent folder
modifier () {
    prevFileCount=$(ls "/calibre/import/${folder}" | wc -l)
    ${importDict[$2]} $1 
    # check if command created a new file, delete if so 
    if [[ $(ls "/calibre/import/${folder}" | wc -l) -gt $prevFileCount ]]; then 
        rm $1
    fi
}

# main loop
while true; do
    for folder in "${!importDict[@]}"; do
        find "/calibre/import/${folder}" -exec modifier {} $folder \; 
        find "/calibre/import/${folder}" -exec calibredb add --with-library /calibre/library {} \; 
    wait $IMPORT_TIME

        





