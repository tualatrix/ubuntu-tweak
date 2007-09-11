#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"
#include "interface.h"

int main(int argc,char **argv)
{
	gchar *initialization_script=PACKAGE_SCRIPTS_DIR"/ubuntu-tweak-initialization";
	GError *error;

#ifdef ENABLE_NLS
	gtk_set_locale();
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
/*
	g_print("Application name: %s\n",str);
	g_print("Program name: %s\n",g_get_prgname());
	g_print("User name: %s\n",g_get_user_name());
	g_print("Real name: %s\n",g_get_real_name());
	g_print("System data dir: %s\n",g_get_system_data_dirs());
	g_print("Host name: %s\n",g_get_host_name());
	g_print("Home dir: %s\n",g_get_home_dir());
	g_print("Tmp dir: %d\n",g_get_tmp_dir());
	g_print("VERSION: %s\n",VERSION);
*/
	window=create_main_window();

	gtk_widget_show(window);
	
	gtk_main();

	return 0;
}
