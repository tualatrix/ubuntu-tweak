#!/bin/bash
#hard shadow
#shutter-plugin
#created by TualatriX <tualatrix@gmail.com>


TEXTDOMAIN=shutter-plugins
TEXTDOMAINDIR=$SHUTTER_INTL
PLUGIN_NAME=$"hard shadow"
PLUGIN_SORT=$"effect"
PLUGIN_TIP=$"a black hard shadow on transparent background"
PLUGIN_EXT="image/png"

if [[ "${1}" = "name" ]];then
   	echo "${PLUGIN_NAME}"
    exit 0
elif [[ "${1}" = "sort" ]];then
    echo "${PLUGIN_SORT}"
    exit 0
elif [[ "${1}" = "tip" ]];then
    echo "${PLUGIN_TIP}"
    exit 0
elif [[ "${1}" = "ext" ]];then
    echo "${PLUGIN_EXT}"
    exit 0
elif [[ "${1}" = "lang" ]];then
    echo "shell"
    exit 0
fi

FILE="${1}"
#WIDTH="${2}"
#HEIGHT="${3}"
#FILEYTPE="${4}"
#GEO="${2}x${3}"

convert "${FILE}" -gravity northwest -background 'rgba(255,255,255,0)' -splice 10x10 \
\( +clone -background gray -shadow 80x3-1-1 \) +swap -background none -mosaic +repage \
\( +clone -background gray -shadow 80x3+5+5 \) +swap -background none -mosaic +repage "${FILE}"

       
exit 0
