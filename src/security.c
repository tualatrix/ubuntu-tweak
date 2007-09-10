#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"

gchar *lockdown_keys[6]={
	"/desktop/gnome/lockdown/disable_command_line",
	"/desktop/gnome/lockdown/disable_lock_screen",
	"/desktop/gnome/lockdown/disable_printing",
	"/desktop/gnome/lockdown/disable_print_setup",
	"/desktop/gnome/lockdown/disable_save_to_disk",
	"/desktop/gnome/lockdown/disable_user_switching",
};

gchar *disable_dir="/desktop/gnome/lockdown";

GtkWidget *create_disable_page()
{
	GtkWidget *main_vbox;
	GtkWidget *vbox;
	GtkWidget *hbox;
	GtkWidget *label;
	GtkWidget *checkbutton;

	main_vbox=gtk_vbox_new(FALSE,10);
	gtk_widget_show(main_vbox);
	gtk_container_set_border_width(GTK_CONTAINER(main_vbox),5);

	label=gtk_label_new(_("Some options for system security"));
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

	checkbutton=create_gconf_checkbutton(_("Disable command line"),lockdown_keys[0],disable_dir,checkbutton_toggled,NULL);
	gtk_widget_show(checkbutton);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_gconf_checkbutton(_("Disable lock screen"),lockdown_keys[1],disable_dir,checkbutton_toggled,NULL);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_gconf_checkbutton(_("Disable printing"),lockdown_keys[2],disable_dir,checkbutton_toggled,NULL);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_gconf_checkbutton(_("Disable run print setup"),lockdown_keys[3],disable_dir,checkbutton_toggled,NULL);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_gconf_checkbutton(_("Disable save to disk"),lockdown_keys[4],disable_dir,checkbutton_toggled,NULL);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_gconf_checkbutton(_("Disable user switching"),lockdown_keys[5],disable_dir,checkbutton_toggled,NULL);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);

	return main_vbox; 
}

GtkWidget *create_security_notebook()
{
	GtkWidget *notebook;
	GtkWidget *main_vbox;
	GtkWidget *page_label;

	notebook=gtk_notebook_new();
	gtk_notebook_set_tab_pos(GTK_NOTEBOOK(notebook),GTK_POS_TOP);


	main_vbox=create_disable_page();
	gtk_widget_show(main_vbox);
	page_label=gtk_label_new(_("Some Security function"));
	gtk_widget_show(page_label);

	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),main_vbox,page_label);		

	return notebook;
}

