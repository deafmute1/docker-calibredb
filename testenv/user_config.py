WATCH = [ 
    {
        "source": "/calibre/import",  # directory to watch (container path)
        "run": 'echo "RAN COMMAND ON {file}"', # command to run on importing file; {file} is replaced by the file path of the imported file
        "remove": False, # If set to true; file in source will be deleted after import
        "pattern": ".*" # Some regex pattern which all files must match to be imported
    }
]