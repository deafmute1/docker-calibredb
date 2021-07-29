#!/bin/sh
for file in /calibre/plugins/build/*; do 
    calibre-customize --add-plugin "$file"
done
[ ! -d /config ] && mkdir /config 
[ ! -d /calibre/plugins/runtime ] && mkdir /calibre/plugins/runtime
exit 0 