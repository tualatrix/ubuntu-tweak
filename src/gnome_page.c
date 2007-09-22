#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"
/*expert mode*/
GtkWidget *expander;
GtkWidget *expert_label;
GtkWidget *expert_box;
GtkWidget *expert_animations;
GtkWidget *expert_lockdownpanel;
GtkWidget *expert_inputunicode;
gpointer present_expert;

gchar *enable_animations_panel="/apps/panel/global/enable_animations";
gchar *enable_animations_gnome="/desktop/gnome/interface/enable_animations";
gchar *key_locked_down_panel="/apps/panel/global/locked_down";
gchar *key_show_input_method_menu="/desktop/gnome/interface/show_input_method_menu";
gchar *key_show_unicode_menu="/desktop/gnome/interface/show_unicode_menu";

gchar *dir_gnome_interface="/desktop/gnome/interface";
gchar *dir_panel_global="/apps/panel/global";

void show_expert_animations(GtkWidget *widget,gpointer data)
{
	if(present_expert!=expert_animations){
		gtk_widget_hide(present_expert);
		expert_animations=create_expert_with_string(_("It seems that if you disable this option, GNOME will more faster"));
		gtk_widget_show(expert_animations);
		present_expert=expert_animations;
		gtk_box_pack_start(GTK_BOX(expert_box),expert_animations,FALSE,FALSE,0);
	}
}

void show_expert_lockdownpanel(GtkWidget *widget,gpointer data)
{
	if(present_expert!=expert_lockdownpanel){
		gtk_widget_hide(present_expert);
		expert_lockdownpanel=create_expert_with_string(_("Check this button if you don't want your gnome-panel to be changed."));
		gtk_widget_show(expert_lockdownpanel);
		present_expert=expert_lockdownpanel;
		gtk_box_pack_start(GTK_BOX(expert_box),expert_lockdownpanel,FALSE,FALSE,0);
	}
}

void show_expert_inputunicode(GtkWidget *widget,gpointer data)
{
	if(present_expert!=expert_inputunicode){
		gtk_widget_hide(present_expert);
		expert_inputunicode=create_expert_with_string(_("Right click menu in the editable area you will find this."));
		gtk_widget_show(expert_inputunicode);
		present_expert=expert_inputunicode;
		gtk_box_pack_start(GTK_BOX(expert_box),expert_inputunicode,FALSE,FALSE,0);
	}
}

GtkWidget *create_gnome_page()
{
	GtkWidget *main_vbox;
	GtkWidget *vbox;
	GtkWidget *hbox;
	GtkWidget *label;
	GtkWidget *checkbutton;

	main_vbox=gtk_vbox_new(FALSE,5);
	gtk_widget_show(main_vbox);
	gtk_container_set_border_width(GTK_CONTAINER(main_vbox),5);

	label=gtk_label_new(NULL);
	gtk_label_set_markup(GTK_LABEL(label),_("<b>GNOME Animations</b>"));
	gtk_misc_set_alignment(GTK_MISC(label),0,0);
	gtk_widget_show(label);
	gtk_box_pack_start(GTK_BOX(main_vbox),label,FALSE,FALSE,0);

	hbox=gtk_hbox_new(FALSE,5);
	gtk_widget_show(hbox);
	gtk_box_pack_start(GTK_BOX(main_vbox),hbox,FALSE,FALSE,0);

	label=gtk_label_new(" ");
	gtk_widget_show(label);
	gtk_box_pack_start(GTK_BOX(hbox),label,FALSE,FALSE,0);

	vbox=gtk_vbox_new(FALSE,5);
	gtk_widget_show(vbox);
	gtk_box_pack_start(GTK_BOX(hbox),vbox,FALSE,FALSE,0);

	checkbutton=create_gconf_checkbutton(_("Enable GNOME Animations Panel"),enable_animations_panel,dir_panel_global,checkbutton_toggled,show_expert_animations);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_gconf_checkbutton(_("Enable GNOME Animations Effect"),enable_animations_gnome,dir_gnome_interface,checkbutton_toggled,show_expert_animations);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_gconf_checkbutton(_("Complete lockdown the panel "),key_locked_down_panel,dir_panel_global,checkbutton_toggled,show_expert_lockdownpanel);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_gconf_checkbutton(_("Show input method menu in the right-click"),key_show_input_method_menu,dir_gnome_interface,checkbutton_toggled,show_expert_inputunicode);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);	

	checkbutton=create_gconf_checkbutton(_("Show unicode method menu in the right-click"),key_show_unicode_menu,dir_gnome_interface,checkbutton_toggled,show_expert_inputunicode);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);	

/*expander*/
	expander=gtk_expander_new_with_mnemonic(_("Need some help? Click here!"));
	gtk_widget_show(expander);
	g_signal_connect(G_OBJECT(expander),"activate",G_CALLBACK(expander_change),NULL);
	gtk_box_pack_end(GTK_BOX(main_vbox),expander,FALSE,FALSE,0);

	expert_box=gtk_vbox_new(FALSE,0);
	gtk_widget_set_size_request(GTK_WIDGET(expert_box),200,100);
	gtk_widget_show(expert_box);
	gtk_container_add(GTK_CONTAINER(expander),expert_box);

	return main_vbox; 
}
