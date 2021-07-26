""" This is a user editable config, in full python format (i.e, this is ran as python code)
    The intention of this file is to allow users to define their list of WATCH dictionaries. 
    This file is to be located at the location defined by environmnetal variable IMPORTER_CONFIG_PATH, 
    or if that is unset, it defaults to ./config.py (where . is the directory that app/config.py is located). 
"""

""" You can set these here, or anywhere else you can set system environmental variables (i.e. in docker run/compose)    
    NB: os.environ is preferable to os.putenv, as setting via os.environ is reflected both in the os.environ dictionary 
    (which is loaded at python startup) and in the actual system envrionment (as os.putenv() is called when this mapping is updated).
"""
import os
os.environ["IMPORT_MODE"] = "NEW"
os.environ["LOG_LEVEL"] = "INFO"

""" You can set a single watch item using env vars, SOURCE, PROCESS, MOVE, FILTER as well. In such case, ignore the need for Path() and re.compile().
    The only _required_ value is source. remove defaults to False, filter will be set to '.*' and process will be skipped
"""
# Some predefined regex filters you may find useful - feel free to edit
FILTER_EBOOK_EXT = r'.*\.(epub|lrf|lrx|djvu|pdb|fb2|ibooks|azw|azw3|kf8|kf|mobi|lit|htm|html|pdf|txt|rtf|prc)$'
FILTER_COMIC_EXT = r'.*\.(cbr|cbz|cb7|cbt|cba|7z|zip|rar|tar.*|rar|jpg|jpeg|png)$'
WATCH = [ 
    {
        "source": "/path/to/directory",  
        "process": "command options {file} options", 
        "remove": False,
        "pattern": "regex pattern"
    }, 
    { 
        # as above   
    }
]