# stdlib
from pathlib import Path 
import os 
from runpy import run_path
import re 
import logging
# internal 
import exceptions

LOG_LEVEL = getattr(logging, os.getenv('LOG_LEVEL').upper())
CALIBRE_LIBRARY = os.getenv('CALIBRE_LIBRARY', '/calibre/library')
CALIBRE_ADD_COMMAND = os.getenv('CALIBRE_ADD_COMMAND', ['calibredb', 'add', '--auto-merge']).extend(['--with-library', CALIBRE_LIBRARY])
CALIBRE_PLUGIN_DIR = os.getenv('CALIBRE_PLUGIN_DIR', '/calibre/plugins/runtime')
METADATA_DB = os.path.join(CALIBRE_LIBRARY, 'metadata.db')
DEFAULT_METADATA_DB = os.getenv('DEFAULT_METADATA_DB', '/calibre/metadata.default.db')
LIBRARY_UID = int(os.getenv('LIBRARY_UID', 1000))
LIBRARY_GID = int(os.getenv('LIBRARY_GID', 1000))
UMASK = oct(os.getenv('UMASK_SET', '0o22'))  # needs to be passed as a decimal

CONFIG_PATH = Path(os.getenv("IMPORTER_CONFIG_PATH", "./watchcfg.py"))
if not CONFIG_PATH.is_file(): 
    raise exceptions.BadConfigValueException("{} is invalid value for environment variable IMPORTER_CONFIG_PATH, as it is not a path to a file".format(CONFIG_PATH))

IMPORT_MODE = os.getenv("IMPORT_MODE", "NEW")
VALID_IMPORT_MODES = ("NEW", "ALL", "ONESHOT")
IMPORT_ALL_TIMER = int(os.getenv("IMPORT_ALL_TIMER", 15))
if IMPORT_MODE not in VALID_IMPORT_MODES: 
    raise exceptions.BadConfigValueException("{} is invalid value for environment variable IMPORT_MODE".format(IMPORT_MODE))

WATCH = run_path(CONFIG_PATH)["WATCH"]
VALID_WATCH_DICT_KEYS = ("source", "process", "move", "pattern")

if (not isinstance(WATCH, list) or any((not isinstance(e, dict) for e in WATCH))): 
    raise exceptions.BadConfigValueException("Malformed data structure or types in WATCH value")

if os.getenv('SOURCE') is not None: 
    WATCH.append({key: os.getenv(key.upper()) for key in VALID_WATCH_DICT_KEYS if key is not None})

for i, rule in enumerate(WATCH):     
    source = Path(rule.get('source'))
    WATCH[i]['source'] = source
    if not source.is_dir():
        raise exceptions.BadConfigValueException('Ruleset {} has source value that is not a directory'.format(i))

    if rule.get('run', None) is None: 
        WATCH[i]['run'] = None 

    if rule.get('remove', None) is None: 
        WATCH[i]['remove'] = False 
    rule = rule.get('pattern', None)
    if rule is None: 
        WATCH[i]['pattern'] = re.compile(r'.*')
    else: 
        WATCH[i]['pattern'] = re.compile(rule)