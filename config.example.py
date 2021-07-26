# required imports, do not remove
from pathlib import Path 
import re 
import os 

""" This is a user editable config, in full python format (i.e, this is ran as python code)
    The intention of this file is to allow users to define their list of WATCH dictionaries. 
    This file is to be located at the location defined by environmnetal variable IMPORTER_CONFIG_PATH, 
    or if that is unset, it defaults to ./config.py (where . is the directory that importer/config.py is located). 
"""

""" You can set this here, or anywhere else you can set system environmental variables (i.e. in docker run/compose)
    
    NB: os.environ is preferable to os.putenv, as setting via os.environ is reflected both in the os.environ dictionary 
    (which is loaded at python startup) and in the actual system envrionment (as os.putenv() is called when this mapping is updated).
"""
os.environ["IMPORT_MODE"] = "NEW"

WATCH = [ 
    {
        "source": Path("/path/to/directory"), 
        "destination": Path("/path/to/directory"), 
        """ number of directories to be maintained when copying: 
            e.g. if set to 2, there will exist a source/one/two/three and a destination/one/two, but not a destination/one/two/three 
            All files in deeper than two (e.g. in three) will be flattened into two. 
            Use 0 to disable """
        "flatten" : 0, 
        "process": "command options {file} options", 
        "move": False, # False = copy 
        "filter": re.compile("regex pattern")
    }, 
    { 
        # as above   
    }
]