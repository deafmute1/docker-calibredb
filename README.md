# docker-calibredb
calibredb is a docker image intended to provide a headless calibre library for use with calibre-web, COPS or similar. It supports automatic imports from a mounted host directory, with the ability to run custom modification via shell commands to the files prior to import based on subfolders. All relevant file types are supported, except multi-file versions of single library titles, such as unarchived manga. Currently, the image provides access to the following packages/binaries which can be used to modify files:

- [calibre](https://manual.calibre-ebook.com/generated/en/cli-index.html)
- [Kindle Comic Converter/KCC](https://github.com/ciromattia/kcc)

## Configuration:
Please refer to docker-compose.yaml.example for an (my) example deployment. You need to modify import.config per your own requirements in a persistent mount point. A default import.config is created on first run if you don't create one initally. It is impossible to headlessly initalise the calibre database (metadata.db) so a pre-created empty metadata.db file has been supplied under /image_root/calibre/defaults/metadata.db and will be copied into place if the user doesn't supply their own from an existing library.

Please note, imported files are removed from mount. This is because using inotify or date created can be unreliable to determine if a file is new. Also you should not download directly into the mount, as it will try to import partially downloaded files. Please see host-helper-scripts for some helper scripts to automate moving files to the mount, modify for your use case if necessary. 

### Mounts: 
    | Container mount point | Function |
    | :----: | --- |
    | /calibre/library | the calibre library, where metadata.db is located |
    | /calibre/import | the location for import folders |
    | /calibre/config | contains import.config and log files |
    
### Environmental variables: 
    | Variable(=Default) | Function | 
    | :----: | --- |
    | UMASK_SET=022 | umask value for entrypoint functions | 
    | IMPORT_TIME=10m | How long to wait before looking for files to import. A value to be understood by `sleep` (integer{h,m,s}). |


### import.config
This goes in /image_root/calibre/config/import.config 
The recommended way to use this file is to mount from host, but you can place it before build if you wish

 Each line in this file is a config for an import rule as such:
       `<subfolder of /calibre/import> <command with arguments>`
This assumes that the command is run as `<command with arguments> <input file> `
You can chain commands using ;, &&, || etc
Or you can point to a shell script, in which case please refer to the file as $1.
Do not wrap command in "" unless you want to pass no command (as below).

# default config with a single import directory with no modification on files
` default "" `