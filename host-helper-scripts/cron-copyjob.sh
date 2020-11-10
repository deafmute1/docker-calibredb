#!/bin/bash
# Takes a root download path ($1) and looks for new items to copy in first level subdirectories
# These files are copied to the desination path ($2), maintaining the first level subdirectory
# $3 specifies how old items to be included are (a integer, representing minutes). Match this to a cron job.

jobTimer=$(( ("$3" + 1) * -1 ))

# parsing `find` into `for` is bad apparently, use while read instead
# on find -mmin: use a negative value to find files newer then the positive value.
while read -r subDir; do
    if [[ ! -f "${2}/${subDir}" ]]; then 
        mkdir -p "${2}/${subDir}"
    fi
    find "$subDir" -type f  -mmin "$jobTimer" -exec rsync -a --ignore-existing {} "${2}/${subDir}" \;
done < <(find "$1" -mindepth 1 -maxdepth 1 -type d)