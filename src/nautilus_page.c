#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"

gchar *key_show_advanced_permissions="/apps/nautilus/preferences/show_advanced_permissions";
gchar *key_burnproof="/apps/nautilus-cd-burner/burnproof";
gchar *key_overburn="/apps/nautilus-cd-burner/overburn";

gchar *key_nautilus_dir="/apps/nautilus/preferences";
gchar *key_cd_burner_dir="/apps/nautilus-cd-burner";


GtkWidget *create_nautilus_page()
{
	GtkWidget *main_vbox;
	GtkWidget *vbox;
	GtkWidget *hbox;
	GtkWidget *label;
	GtkWidget *separator;
	GtkWidget *checkbutton;

	main_vbox=gtk_vbox_new(FALSE,10);
	gtk_widget_show(main_vbox);
	gtk_container_set_border_width(GTK_CONTAINER(main_vbox),10);

	label=gtk_label_new(_("Setting your nautilus behavior"));
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

	checkbutton=create_gconf_checkbutton(_("Show advanced permissions at file property"),key_show_advanced_permissions,key_nautilus_dir,checkbutton_toggled,NULL);
	gtk_widget_show(checkbutton);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);

	GtkWidget *frame;
	frame=gtk_frame_new(_("CD Burner"));
	gtk_widget_show(frame);
	gtk_box_pack_start(GTK_BOX(main_vbox),frame,FALSE,FALSE,0);
	
	vbox=gtk_vbox_new(FALSE,0);
	gtk_widget_show(vbox);
	gtk_container_add(GTK_CONTAINER(frame),vbox);

	checkbutton=create_gconf_checkbutton(_("Enable Burnproof option"),key_burnproof,key_cd_burner_dir,checkbutton_toggled,NULL);
	gtk_widget_show(checkbutton);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_gconf_checkbutton(_("Enable overburn"),key_overburn,key_cd_burner_dir,checkbutton_toggled,NULL);
	gtk_widget_show(checkbutton);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);

	return main_vbox; 
}
