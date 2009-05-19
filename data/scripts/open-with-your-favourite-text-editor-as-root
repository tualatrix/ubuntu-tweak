#!/bin/bash
IFS='
'
i=1
for url in $NAUTILUS_SCRIPT_SELECTED_URIS
do
	if [ -n "`echo $url | grep 'file:///'`" ];then
		script-worker open `echo "$NAUTILUS_SCRIPT_SELECTED_FILE_PATHS" | cut -f$i -d'
'` root &
	else
		script-worker open "$url" root &
	fi
	i=$(($i+1))
done
