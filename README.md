# docker-calibredb
calibredb is a docker image intended to provide a headless calibre library for use with calibre-web, COPS or similar. It supports automatic imports from a mounted host directory(s), with the ability filter files based on regex patterns and to run custom modification via shell commands to the files prior to import based on subfolders. It includes the calibre plugin DeDRM prebuilt into the image, and allows users to mount their own plugins into the image. Currently, the image provides access to the following packages/binaries (in addition to a regular ubuntu hirsuite install) which can be used to modify files before import:

- [calibre](https://manual.calibre-ebook.com/generated/en/cli-index.html)
- [Kindle Comic Converter/KCC](https://github.com/ciromattia/kcc) (`kcc-c2e` and `kcc-c2p`)

**Get it on [docker hub](https://hub.docker.com/repository/docker/deafmute/calibredb)**, using tags:
- `deafmute/calibredb:latest`: builds from master branch.
- `deafmute/calibredb:testing`: builds from testing branch (not intended for real world use).
- `deafmute/calibredb:version-*`: builds builds from tagged releases.

## Configuration:
Users should set environmnetal variables and mount points as required in `docker-compose.yaml` or `docker run`, then view [user_config.example.py](user_config.example.py) in order to set an import rule, which comprises a source directory, regex pattern, remove boolean and import command (users can also set a single rule using environmental variables).

### user_config.py
This file needs to contain a variable `WATCH` which is equal to a list of dictionaries with keys:
-  `source` containing a string representing the path to import files from. (Required)
-   `run` containg a string (which may use the token {file} to represent the filepath of each imported file) representing a command to be run at import of each file. (Optional, default is to skip it)
-   `remove` containing a boolean, representing whether files in `source` should be deleted after import. (Optional, deafult is False) 
-   `pattern` containing a string representing a python regex pattern (Optional, default is to skip checking it)

### Import Modes
There are three import modes currently:
- NEW: monitors `source` directory for new files recursively and imports them (default) 
- ALL: Every `$IMPORT_ALL_TIMER` minutes, imports all files in `source`  
- ONESHOT: Import all files in `source` once, then exit

Please note, calibre is capable of adding literally any file - I've tested things like database files and binaries, and it can add them fine. It does not seem to run any validation on the files as valid ebooks. As such, there is no logging feedback on success of the command, it is assumed that `calibredb add` is always sucessful. The user should be aware then, that any file addded to `source` will be imported, unless they make use of `pattern`. 

There is no support for single entries spread across many files (i.e. unpacked comic books), this is due to calibre itself. Packed comic book archives should work fine.

### Environmental variables: 

| Variable | Default | Description |  Valid values | 
| --- | --- | --- | --- |
| LOG_LEVEL | "INFO" | Set log verbosity | "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL" | 
| CALIBRE_LIBRARY | "/calibre/library" | Location of calibre library | Any directory |
| CALIBRE_PLUGIN_DIR | "/calibre/plugins/runtime" | Location of folder containing plugins to be installed at container start | Any directory | 
| LIBRARY_UID | 1000 | UID of user who owns the library (i.e. who should own files in CALIBRE_LIBRARY) | Any 32-bit int | 
| LIBRARY_GID | 1000 | AS above, but for GID | Any 32-bit-int |
| UMASK | 18 | The umask to run the program under (i.e. to create new files under), as an integer. Reminder that this represents the _unset_ permission bits of the resulting file (i.e. 18 (octal 022) results in file with perms 492 (octal 755)) | 0-511 |
| USER_CONFIG_PATH | "/config/user_config.py" | Location of the user import rules, as described in [config.example.py](config.example.py) | Valid file path | 
| TRANSFER_TIMEOUT | 15 | How long (in minutes) the program waits for a file to copy (before attempting import) before timeing out and skiping that file | Any int |  
| IMPORT_MODE | "NEW" | See [import modes](#import-modes) | "NEW", "ALL", "ONESHOT" | 
| IMPORT_ALL_TIMER | 10 | How long (in minutes) should the program wait between running import under `IMPORT_MODE=ALL` | Any int | 

### Mount points
See [above](#environmental-variables) in regards to `CALIBRE_LIBRARY`, `CALIBRE_PLUGIN_DIR`, `USER_CONFIG_PATH`. See [config.example.py](config.example.py) in regards to setting the location of the source directories to import new files from. In addition, there are some relevant static paths: 
| Path | Function |
| --- | --- |
| `/root/.config/calibre` | Location of calibre's settings folder |

## TODO 
- Allow users to add their own packages for use in run commands, like was done with plugins. 
- Allow users to set IMPORT_MODE per rule 