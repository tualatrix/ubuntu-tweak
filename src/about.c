#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"

void show_about(GtkWidget widget,gpointer data)
{
	gchar*  authors[] = {"TualatriX <tualatrix@gmail.com>",NULL}; 

	gtk_show_about_dialog (NULL,
	"name","Ubuntu Tweak",
	"authors", authors,
	"website", "http://ubuntu-tweak.com",
	"copyright", "Copyright © 2007 TualatriX",
	"comments", _("专为Ubuntu系统开发的设置优化工具"),
	"version", PACKAGE_VERSION,
	NULL);
}
