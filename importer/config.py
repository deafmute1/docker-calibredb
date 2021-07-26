#stdlib
from pathlib import Path 
import os 
from runpy import run_path
#internal 
import exceptions

CONFIG_PATH = Path(os.getenv("IMPORTER_CONFIG_PATH", "./watchcfg.py"))
if not CONFIG_PATH.is_file(): 
    raise exceptions.BadConfigValueException("{} is invalid value for environment variable IMPORTER_CONFIG_PATH, as it is not a path to a file".format(IMPORTER_CONFIG_PATH))

IMPORT_MODE = os.getenv("IMPORT_MODE", "ALL")
if IMPORT_MODE not in (NEW, ALL): 
    raise exceptions.BadConfigValueException("{} is invalid value for environment variable IMPORT_MODE".format(IMPORT_MODE))

WATCH = run_path(CONFIG_PATH)["WATCH"]
#TODO Validate WATCH values better than this.
if ( not isinstance(WATCH, list) or any((not isinstance(e, dict) for e in WATCH))): 
    raise exceptions.BadConfigValueException("Malformed data structure or types in WATCH value")