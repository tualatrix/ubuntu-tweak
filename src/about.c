#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"


void show_about(GtkWidget *widget,gpointer data)
{
	gchar*  authors[] = {"TualatriX <tualatrix@gmail.com>",NULL}; 

	gtk_show_about_dialog(NULL,
	"name","Ubuntu Tweak",
	"authors", authors,
	"website", "http://linuxdesktop.cn",
	"copyright", "Copyright © 2007 TualatriX",
	"comments", _("Ubuntu Tweak is tool for Ubuntu that makes it easy to config your system and desktop."),
	"version", PACKAGE_VERSION,
	NULL);
}

