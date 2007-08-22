#include <glib/gi18n.h>
#include "interface.h"

#define GETTEXT_PACKAGE "ubuntu-tweak"
#define LOCALEDIR "./locale"

int main(int argc,char **argv)
{
	GtkWidget *window;
	GError *err=NULL;
	/*g_spawn_command_line_async("scripts/ubuntu-tweak-script",NULL);
	sleep(1);*/

	bindtextdomain (GETTEXT_PACKAGE, LOCALEDIR);
	bind_textdomain_codeset (GETTEXT_PACKAGE, "UTF-8");
	textdomain (GETTEXT_PACKAGE);
	gtk_init(&argc,&argv);

	window=create_main_window();

	gtk_widget_show(window);
	
	gtk_main();

	return 0;
}
