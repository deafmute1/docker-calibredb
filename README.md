# docker-calibredb
calibredb is a docker image intended to provide a headless calibre library for use with calibre-web, COPS or similar. It supports automatic imports from a mounted host directory, with the ability to run custom modification via shell commands to the files prior to import based on subfolders. All relevant file types are supported, except multi-file versions of single library titles, such as unarchived manga. Currently, the image provides access to the following packages/binaries which can be used to modify files:

- [calibre](https://manual.calibre-ebook.com/generated/en/cli-index.html)
- [Kindle Comic Converter/KCC](https://github.com/ciromattia/kcc)

Includes calibre plugin DeDRM as well (TODO: allow user to add their own plugins).

## Configuration:
Please refer to `docker-compose.yaml.example` for example deployment (my personal deployment). You need to modify import.config per your own requirements. It is impossible to headlessly initalise the calibre database so a pre-created, empty metadata.db file has been supplied under `/image_root/calibre/defaults/metadata.db` and will be copied into place if there is no existing metadata.db. I used the same version as the image to create `metadata.db` - you may have issues in newer versions (v5+) as this image is still running the python2 version of calibre (v3.39.1).

Please note, imported files are deleted from mount. This is because using inotify or date created can be unreliable to determine if a file is new and there is no reason I can see why the files would need to remain after import in the import folder, if you run helper scripts as needed to copy files (see host-helper-scripts). 

### Mounts: 

Container mount point | Function 
--- | --- 
/calibre/library | the calibre library, where metadata.db is located 
/calibre/import | the location for import folders as defined by import.config
/calibre/config | contains import.config 
/calibre/config/bash.timer.d | contains bash scripts to be run every $IMPORT_TIME
/calibre/config/bash.setup.d | contains bash scripts to be run on deploy
    
### Environmental variables: 

| Variable(=Default) | Function | 
| --- | --- |
| UMASK_SET=022 | umask value for entrypoint functions | 
| IMPORT_TIME=10m | How long to wait before looking for files to import. A value to be understood by `sleep` (`$integer{h,m,s}`). |


### import.config:
This goes in /image_root/calibre/config/import.config. The recommended way to use this file is to mount from host, but you can place it there before build if you wish.

Each line in this file is an an import rule like: `<subfolder of /calibre/import> <command with arguments>`
- `entrypoint.sh` assumes that the command is run as `<command with arguments> <input file> `
- You can chain commands using ;, &&, || etc. Or you can point to a shell script, in which case please refer to the file as $1.
- Do not wrap command in " " unless you want to pass no command (as below).  You can do so if you want a folder with a space, but why?

``` sh
# default config with a single import directory with no modification on files
 default "" 

# config for converting manga to mobi
manga kcc-c2e -m -f MOBI
 ``` 