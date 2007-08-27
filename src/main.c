#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"
#include "interface.h"

int main(int argc,char **argv)
{
	GtkWidget *window;
	gchar *initialization_script=PACKAGE_SCRIPTS_DIR"/ubuntu-tweak-initialization";
	GError *error;

#ifdef ENABLE_NLS
  bindtextdomain (GETTEXT_PACKAGE, PACKAGE_LOCALE_DIR);
  bind_textdomain_codeset (GETTEXT_PACKAGE, "UTF-8");
  textdomain (GETTEXT_PACKAGE);
#endif
	gtk_init(&argc,&argv);

        g_spawn_command_line_sync(g_strconcat("bash ",initialization_script,NULL),
                                NULL,
                                NULL,
                                NULL,
                                &error);

	g_print("GETTEXT_PACKAGE: %s\n",GETTEXT_PACKAGE);
	g_print("PACKAGE_LOCALE_DIR: %s\n",PACKAGE_LOCALE_DIR);
	g_print("PACKAGE_DOC_DIR: %s\n",PACKAGE_DOC_DIR);
	g_print("PACKAGE_DATA_DIR: %s\n",PACKAGE_DATA_DIR);
	g_print("PACKAGE_PIXMAPS_DIR: %s\n",PACKAGE_PIXMAPS_DIR);
	g_print("PACKAGE_MENU_DIR: %s\n",PACKAGE_MENU_DIR);
	g_print("PACKAGE_SOURCE_DIR: %s\n",PACKAGE_SOURCE_DIR);
	g_print("PACKAGE_NAME: %s\n",PACKAGE_NAME);
	g_print("PACKAGE: %s\n",PACKAGE);
	g_print("PACKAGE_TARNAME: %s\n",PACKAGE_TARNAME);
	g_print("PACKAGE_VERSION: %s\n",PACKAGE_VERSION);
	g_print("STDC_HEADERS: %d\n",STDC_HEADERS);
	g_print("VERSION: %s\n",VERSION);

	window=create_main_window();

	gtk_widget_show(window);
	
	gtk_main();

	return 0;
}
