""" This is a user editable config, in full python format (i.e, this is ran as python code)
    The intention of this file is to allow users to define their list of WATCH dictionaries. 
    This file is to be located at the location defined by environmnetal variable CONFIG_PATH, 
    or if that is unset, it defaults to /config/user_config.py.
    You can set a single watch item using env vars, SOURCE, RUN, MOVE, FILTER as well. 
    The only _required_ value is source. remove defaults to False, filter will be set to '.*' and run will be skipped
"""
# Some predefined regex filters you may find useful - feel free to edit
FILTER_EBOOK_EXT = r'.*\.(epub|lrf|lrx|djvu|pdb|fb2|ibooks|azw|azw3|kf8|kf|mobi|lit|htm|html|pdf|txt|rtf|prc|md)$'
FILTER_COMIC_EXT = r'.*\.(cbr|cbz|cb7|cbt|cba|7z|zip|rar|tar.*|rar|jpg|jpeg|png)$'
WATCH = [ 
    {
        "source": "/path/to/directory",  # directory to watch
        "run": "command options {file} options", # command to run on importing file; {file} is replaced by the file path of the imported file
        "remove": False, # If set to true; file in source will be deleted after import
        "pattern": "regex pattern" # Some regex pattern which all files must match to be imported
    }, 
    { 
        # etc  
    }
]