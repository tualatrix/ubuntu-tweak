#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"


gchar *enable_animations_panel="/apps/panel/global/enable_animations";
gchar *enable_animations_gnome="/desktop/gnome/interface/enable_animations";


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


	label=gtk_label_new("设置GNOME动画");
	gtk_widget_show(label);
	gtk_box_pack_start(GTK_BOX(main_vbox),label,FALSE,FALSE,0);

	hbox=gtk_hbox_new(FALSE,10);
	gtk_widget_show(hbox);
	gtk_box_pack_start(GTK_BOX(main_vbox),hbox,FALSE,FALSE,0);

	label=gtk_label_new(" ");
	gtk_widget_show(label);
	gtk_box_pack_start(GTK_BOX(hbox),label,FALSE,FALSE,0);

	vbox=gtk_vbox_new(FALSE,10);
	gtk_widget_show(vbox);
	gtk_box_pack_start(GTK_BOX(hbox),vbox,FALSE,FALSE,0);

	checkbutton=create_gconf_checkbutton("启用面版动画效果",enable_animations_panel,"/apps/panel/global",checkbutton_toggled,NULL);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_gconf_checkbutton("启用GNOME动画效果",enable_animations_gnome,"/desktop/gnome/interface",checkbutton_toggled,NULL);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);

	return main_vbox; 
}
