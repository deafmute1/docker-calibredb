#!/bin/bash

# FUNCTIONS
function CopySourceFileToAll() {
    # $1 = absolute path to a source file  
    # $2 = subfolder it was found in
  while IFS= read -r -d ';' matchsub; do
     [[ ! -d "$matchsub" ]] && mkdir -p "$matchsub"
    cp "$1" "${matchsub}/${2}"
  done <<< "$matchsubs"

  while IFS=':' read -r -d ';' dd_sub dd_dest; do
    if [[ "$dd_sub" == "$2" ]]; then
      [[ ! -d "$dd_dest" ]] && mkdir -p "$dd_dest"
      cp "$1" "$dd_dest"
    fi
  done <<< "$directdir" 

}

function help() {
  echo "
  cron-copyjob.sh for deafmute1/docker_calibredb v2
  Ethan Djeric <me@ethandjeric.com>

  Monitors a source path for new files in some time interim, and copies new files to given directories. 
  Includes logic to match top level directory hierarchies between source and destination.
  Intended to be used with environmental variable DELETE_IMPORTED=true in calibredb, and with interim 
  matching a cron job calling the script. Also can be used with other servers such as komga.
  
  Usage: /path/to/cron-copyjob.sh INTERIM SOURCE [OPTION(S)]

  INTERIM and SOURCE are required, in addition to one or more of -m or -d.

  Positional Arguments:
  INTERIM(*)    Time (in minutes) to look for new files (i.e. crontab job timer)
  SOURCE(*)     Absolute path to a source directory, intended to be a top level directory to some high level
                directory containing subfolders with trees of unlimted depth that are flattened and move to one 
                or more destinations.

   Option(s):
  -h, --help                    Print this information.

  -m,--matchsubs [PATH]         Absolute path to a top level directory to copy files at *(2) in SOURCE/*(1)/*(2) to 
                                PATH/*(1)/*(2), where any files in subfolders of *(2) are flattened into *(2) and copied.

  -d, --directdir [SUBDIR] [DIR]  Just copy flattened files from [SUBDIR] (a directory in SOURCE), to some absolute path 
                                  specifed by [DIR]
  "
}

# MAIN 
# setup env
set -euxo pipefail
export -f CopySourceFileToAll 

case "$1" in 
  -h|-help|help) 
    help 
    exit 0 ;;

  *) 
    timer="$1" 
    src="$2" 
    shift 2;;
esac

matchsubs=""
directdir=""
while [[ "$#" -gt 0 ]]; do 
  case "$1" in
    -m|--matchsubs)
      [[ ! "$2" == -* ]] && echo "bad input; please provide path(s) after specifying -m/--matchsub or -d/--absolutedir"
      matchsubs="${matchsubs}${2};"
      shift 2 ;;
    
    -d,--directdir)
      [[ ! "$2" == -* || ! "$3" == -* ]] && echo "bad input; please provide path(s) after specifying -m/--matchsub or -d/--absolutedir" 
      directdir="${directdir}${2}:${3};"
      shift 3 ;;
  esac
done

# use a negative value for `find -mmin` to find files newer then the positive value.
# add +5 for safety - missing a file will result in it never being imported, but copying twice will just waste a little time in entrypoint.sh
job_timer=$(( ("$timer" + 5) * -1 ))
# parsing `find` into `for` is bad apparently, use while read instead
while read -r sub_path; do
  folder_name=$(basename "$sub_path")
  find "$sub_path" -type f  -mmin "$job_timer"  -exec bash -c "copyToArray '$1' '$folder_name'"_ {} \;
done < <(find "$src" -mindepth 1 -maxdepth 1 -type d)
