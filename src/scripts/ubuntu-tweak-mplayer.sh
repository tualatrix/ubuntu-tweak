#!/bin/bash

#首先取出gui.conf文件中有vo-driver字段的行，然后交给awk处理，取出由"分隔的第二个字段
VO_DRIVER=`grep "vo_driver" ~/.mplayer/gui.conf|awk -F"\"" '{print $2}'`

if [ -z $VO_DRIVER ]; then
	echo $VO_DRIVER
	echo "键值未设置"
	gconftool-2 --set --type boolean /apps/ubuntu-tweak/apps/mplayer/vo_driver false
elif [ $VO_DRIVER = "x11" ]; then
	echo $VO_DRIVER
	echo "键值已设置为x11"
	gconftool-2 --set --type boolean /apps/ubuntu-tweak/apps/mplayer/vo_driver true
else
	echo $VO_DRIVER
	gconftool-2 --set --type boolean /apps/ubuntu-tweak/apps/mplayer/vo_driver false
fi
