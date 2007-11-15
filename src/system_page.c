#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"

GtkWidget *create_system_page()
{
	GtkWidget *main_vbox;
	GtkWidget *vbox;
	GtkWidget *hbox;
	GtkWidget *label;
	GtkWidget *checkbutton;

	main_vbox=gtk_vbox_new(FALSE,10);
	gtk_widget_show(main_vbox);
	gtk_container_set_border_width(GTK_CONTAINER(main_vbox),5);

	label=gtk_label_new(NULL);
	gtk_label_set_markup(GTK_LABEL(label),_("<b>System options</b>"));
	gtk_misc_set_alignment(GTK_MISC(label),0,0);
	gtk_widget_show(label);
	gtk_box_pack_start(GTK_BOX(main_vbox),label,FALSE,FALSE,0);
	
	hbox=gtk_hbox_new(FALSE,10);
	gtk_widget_show(hbox);
	gtk_box_pack_start(GTK_BOX(main_vbox),hbox,FALSE,FALSE,0);
	
	label=gtk_label_new(" ");
	gtk_widget_show(label);
	gtk_box_pack_start(GTK_BOX(hbox),label,FALSE,FALSE,0);

	vbox=gtk_vbox_new(FALSE,0);
	gtk_widget_show(vbox);
	gtk_box_pack_start(GTK_BOX(hbox),vbox,FALSE,FALSE,0);

	IniFile *ini;
	ini = ini_file_open_file("/etc/default/rcS");

	checkbutton=gtk_check_button_new_with_label("不使用UTC时间");
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);
	if (!g_ascii_strcasecmp (ini_file_get_value(ini, "UTC"), "no"))
	{
		gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),TRUE);
	}

	ini_file_free(ini);
	
	return main_vbox; 
}
