#!/bin/bash

#首先取出gui.conf文件中有vo-driver字段的行，然后交给awk处理，取出由"分隔的第二个字段
MPLAYER_GUI_CONF=`echo ~/.mplayer/gui.conf`
VO_DRIVER=`grep "vo_driver" $MPLAYER_GUI_CONF |awk -F"\"" '{print $2}'`

if [ -z $1 ]; then
	if [ -z $VO_DRIVER ]; then
		gconftool-2 --set --type boolean /apps/ubuntu-tweak/apps/mplayer/vo_driver false
	elif [ $VO_DRIVER = "x11" ]; then
		echo $VO_DRIVER
		gconftool-2 --set --type boolean /apps/ubuntu-tweak/apps/mplayer/vo_driver true
	else
		echo $VO_DRIVER
		gconftool-2 --set --type boolean /apps/ubuntu-tweak/apps/mplayer/vo_driver false
	fi

elif [ $1 = "mplayer" ]; then
	MPLAYER_BOOL=`gconftool-2 -g /apps/ubuntu-tweak/apps/mplayer/vo_driver`
	if [ $MPLAYER_BOOL = "true" ] ;then
		gconftool-2 --set --type boolean /apps/ubuntu-tweak/apps/mplayer/vo_driver flase
		sed -e "s/$VO_DRIVER/xv/" $MPLAYER_GUI_CONF > $MPLAYER_GUI_CONF.tmp
		mv $MPLAYER_GUI_CONF.tmp $MPLAYER_GUI_CONF
	else
		gconftool-2 --set --type boolean /apps/ubuntu-tweak/apps/mplayer/vo_driver true
		sed -e "s/$VO_DRIVER/x11/" $MPLAYER_GUI_CONF > $MPLAYER_GUI_CONF.tmp
		mv $MPLAYER_GUI_CONF.tmp $MPLAYER_GUI_CONF
	fi
fi
