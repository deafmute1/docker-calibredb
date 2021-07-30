# stdlib
from pathlib import Path 
import os 
from runpy import run_path
import logging
import re 
# internal 
import exceptions

VALID_CONFIG_VALUES =   ( 'CALIBRE_LIBRARY', 
                        'CALIBRE_ADD_COMMAND', 
                        'CALIBRE_PLUGIN_DIR', 
                        'METADATA_DB', 
                        'DEFAULT_METADATA_DB', 
                        'LIBRARY_UID', 
                        'LIBRARY_GID', 
                        'UMASK',
                        'USER_CONFIG_PATH',
                        'TRANSFER_TIMEOUT',
                        'IMPORT_ALL_TIMER',
                        'IMPORT_MODE',
                        'VALID_IMPORT_MODES',
                        'IMPORT_ALL_TIMER',
                        'WATCH',
                        'VALID_WATCH_DICT_KEYS' )
LOG_LEVEL = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
CALIBRE_LIBRARY = os.getenv('CALIBRE_LIBRARY', '/calibre/library')
CALIBRE_ADD_COMMAND = os.getenv('CALIBRE_ADD_COMMAND', 'calibredb add --automerge overwrite')
CALIBRE_PLUGIN_DIR = os.getenv('CALIBRE_PLUGIN_DIR', '/calibre/plugins/runtime')
METADATA_DB = os.path.join(CALIBRE_LIBRARY, 'metadata.db')
DEFAULT_METADATA_DB = os.getenv('DEFAULT_METADATA_DB', '/calibre/metadata.default.db')
LIBRARY_UID = int(os.getenv('LIBRARY_UID', 1000))
LIBRARY_GID = int(os.getenv('LIBRARY_GID', 1000))
UMASK = int(os.getenv('UMASK_SET', 18)) 
USER_CONFIG_PATH = Path(os.getenv("CONFIG_PATH", "/config/user_config.py"))
TRANSFER_TIMEOUT = int(os.getenv('TRANSFER_TIMEOUT', 15))
IMPORT_ALL_TIMER = int(os.getenv('IMPORT_ALL_TIMER', 10))
IMPORT_MODE = os.getenv("IMPORT_MODE", "NEW")
VALID_IMPORT_MODES = ("NEW", "ALL", "ONESHOT")
IMPORT_ALL_TIMER = int(os.getenv("IMPORT_ALL_TIMER", 15))
WATCH = run_path(USER_CONFIG_PATH)["WATCH"]
VALID_WATCH_DICT_KEYS = ("source", "process", "move", "pattern")

if not USER_CONFIG_PATH.is_file(): 
    raise exceptions.BadConfigValueException("{} is invalid value for environment variable CONFIG_PATH, as it is not a path to a file".format(USER_CONFIG_PATH))

if IMPORT_MODE not in VALID_IMPORT_MODES: 
    raise exceptions.BadConfigValueException("{} is invalid value for environment variable IMPORT_MODE".format(IMPORT_MODE))

if (not isinstance(WATCH, list) or any((not isinstance(e, dict) for e in WATCH))): 
    raise exceptions.BadConfigValueException("Malformed data structure or types in WATCH value")

if os.getenv('SOURCE') is not None: 
    WATCH.append({key: os.getenv(key.upper()) for key in VALID_WATCH_DICT_KEYS if os.getenv(key.upper()) is not None})

for i, rule in enumerate(WATCH):     
    source = Path(rule['source'])
    WATCH[i]['source'] = source
    if not source.is_dir():
        raise exceptions.BadConfigValueException('Ruleset {} has source value that is not a directory'.format(rule))

    WATCH[i]['run'] = rule.get('run', None) 

    if rule.get('remove', None) is None: 
        WATCH[i]['remove'] = False

    WATCH[i]['pattern'] = rule.get('pattern', None)