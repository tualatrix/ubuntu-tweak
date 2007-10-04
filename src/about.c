#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"


void show_about(GtkWidget *widget,gpointer data)
{
	const gchar* authors[] = {
		"TualatriX <tualatrix@gmail.com>",
		NULL
	}; 
	const gchar* artists[] = {
		"Medical-Wei <a790407@hotmail.com> 3D Ubuntu Logo",
		NULL
	};

	gtk_show_about_dialog(NULL,
	"name","Ubuntu Tweak",
	"authors", authors,
	"artists", artists,
	"website", "http://ubuntu-tweak.com",
	"copyright", "Copyright © 2007 TualatriX",
	"comments", _("Ubuntu Tweak is tool for Ubuntu that makes it easy to config your system and desktop."),
	"version", PACKAGE_VERSION,
	NULL);
}

