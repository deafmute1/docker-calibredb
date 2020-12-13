# docker-calibredb
calibredb is a docker image intended to provide a headless calibre library for use with calibre-web, COPS or similar. It supports automatic imports from a mounted host directory, with the ability to run custom modification via shell commands to the files prior to import based on subfolders. It includes the calibre plugin DeDRM prebuilt into the image. All relevant file types are supported, except a single db item spread over multiple files. Currently, the image provides access to the following packages/binaries which can be used to modify files before import:

- [calibre](https://manual.calibre-ebook.com/generated/en/cli-index.html)
- [Kindle Comic Converter/KCC](https://github.com/ciromattia/kcc) (`kcc-c2e` and `kcc-c2p` (do not call them as kcc-*.py))

**Get it on [docker hub](https://hub.docker.com/repository/docker/deafmute/calibredb)**, using autobuild tags:
- `deafmute/calibredb:latest`: autobuilds from master branch.
- `deafmute/calibredb:testing`: autobuilds from testing branch (not intended for real world use).
- `deafmute/calibredb:version-*`: autobuilds builds from tagged releases.

## Configuration:
Please refer to `docker-compose.yaml.example` for example deployment (my personal deployment). You need to modify imports per your own requirements. It is impossible to headlessly initalise the calibre database so a pre-created, empty metadata.db file has been supplied under `/image_root/calibre/defaults/metadata.db` and will be copied into place if there is no existing metadata.db. I used the same calibre version as the image to create `metadata.db` - you may have issues if you bring a metadata.db from newer versions (v5+) as this image is still running the old python2 version of calibre (v3.39.1).

### Mounts: 

Container mount point | Function 
--- | --- 
/calibre/library | the calibre library, where metadata.db is located 
/calibre/import | the location for import folders as defined by imports file
/calibre/config | contains imports and entrypoint.log
/calibre/config/bash.timer.d | contains bash scripts to be run every $IMPORT_TIME (optional)
/calibre/config/bash.setup.d | contains bash scripts to be run on deploy (optional)
    
### Environmental variables: 

| Variable(=Default) | Function | 
| --- | --- |
| UMASK_SET=022 | umask value for entrypoint functions | 
| IMPORT_TIME=10m | How long to wait before looking for files to import (a value to be understood by `sleep`)|
| DELETE_IMPORTED=false | If true, delete files after import (calibre will not import duplicates, but it may cause performance issues later) |
| LIBRARY_UID=1000 | chown library directory to this user |
| LIBRARY_GID=1000 | chown library directory to this group |
| VERBOSE=false | enables highly verbose (set -x) mode for entrypoint.log |

### /calibre/config/imports:
The recommended way to use this file is to mount /calibre/config from host.

Each line in this file is an an import rule as per this syntax: `<a subfolder of /calibre/import (no spaces)> <command with arguments, including spaces where necessary>`
- `entrypoint.sh` assumes that the command is run as `<command with arguments> <input file> `
- You can chain commands using ;, &&, || etc. 
- You can point to a shell script, in which case please refer to the file as variable `$1`.
- Do not use  "", #, " " or empty lines anywhere in this file, it will break things - the file is read in from stdin to an array, it is not a bash file.

**Examples:**

import rule for files in directory /calibre/import/untouched, which runs no modification to files:

`untouched`

import rule for files in directory /calibre/import/manga, which uses to kcc-c2e to generate a kindle-friendly mobi from manga archives:

`manga kcc-c2e -m -f MOBI`