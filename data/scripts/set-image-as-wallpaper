#!/bin/bash

###############################################################################
# Display a fullscreen slideshow of the selected files
###############################################################################
#
# AUTHOR:	Karl Bowden <kbowden@pacificspeed.com.au>
#
# CREDITS:	Brian Connelly <pub@bconnelly.net> - For the slideshow script
#		that I based this script on.
#
# DESCRIPTION:	This script sets the background in Gnome2 the the selected
#		filename.
#
# REQUIREMENTS:	Nautilus file manager
#		Gnome2
#		gdialog, which is usually included in the gnome-utils package
#
# INSTALLATION:	copy to the ~/.gnome2/nautilus-scripts directory
#		
# USAGE:	Select the file that you would like to use as your wallpaper
#		in Nautilus, right click, go to Scripts, and then select this
#		script. You will then be asked to selest how you would like
#		the image displayed.
#
# VERSION INFO:	
#		0.1 (20020928) - Initial public release
#
# COPYRIGHT:	Copyright (C) 2002 Karl Bowden <kbowden@pacificspeed.com.au>
#
# LICENSE:	GNU GPL
#
###############################################################################

WALLPAPER=$(gdialog --title "Wallpaper Options" --radiolist "Picture Options:" 60 100 10 1 Wallpaper on 2 Centered off 3 Scaled off 4 Stretched off 2>&1)

if [ $WALLPAPER = "1" ]; then
	gconftool-2 --type=string --set /desktop/gnome/background/picture_options wallpaper
	gconftool-2 --type=string --set /desktop/gnome/background/picture_filename $NAUTILUS_SCRIPT_SELECTED_FILE_PATHS
fi
if [ $WALLPAPER = "2" ]; then
	gconftool-2 --type=string --set /desktop/gnome/background/picture_options centered
	gconftool-2 --type=string --set /desktop/gnome/background/picture_filename $NAUTILUS_SCRIPT_SELECTED_FILE_PATHS
fi
if [ $WALLPAPER = "3" ]; then
	gconftool-2 --type=string --set /desktop/gnome/background/picture_options scaled
	gconftool-2 --type=string --set /desktop/gnome/background/picture_filename $NAUTILUS_SCRIPT_SELECTED_FILE_PATHS
fi
if [ $WALLPAPER = "4" ]; then
	gconftool-2 --type=string --set /desktop/gnome/background/picture_options stretched
	gconftool-2 --type=string --set /desktop/gnome/background/picture_filename $NAUTILUS_SCRIPT_SELECTED_FILE_PATHS
fi
