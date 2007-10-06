#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"

static gchar *show_desktop="/apps/nautilus/preferences/show_desktop";
static gchar *computer_icon_name="/apps/nautilus/desktop/computer_icon_name";
static gchar *computer_icon_visible="/apps/nautilus/desktop/computer_icon_visible";
static gchar *documents_icon_name="/apps/nautilus/desktop/documents_icon_name";
static gchar *documents_icon_visible="/apps/nautilus/desktop/documents_icon_visible";
static gchar *home_icon_name="/apps/nautilus/desktop/home_icon_name";
static gchar *home_icon_visible="/apps/nautilus/desktop/home_icon_visible";
static gchar *network_icon_visible="/apps/nautilus/desktop/network_icon_visible";
static gchar *trash_icon_name="/apps/nautilus/desktop/trash_icon_name";
static gchar *trash_icon_visible="/apps/nautilus/desktop/trash_icon_visible";
static gchar *volumes_visible="/apps/nautilus/desktop/volumes_visible";
static gchar *use_home_as_desktop="/apps/nautilus/preferences/desktop_is_home_dir";
static gchar *nautilus_desktop_dir="/apps/nautilus/desktop";
static gchar *nautilus_preferences_dir="/apps/nautilus/preferences";

GtkWidget *expander;
GtkWidget *expander_label;

GtkWidget *desktop_hbox1;
GtkWidget *desktop_hbox2;
GtkWidget *desktop_hbox3;
GtkWidget *desktop_hbox4;

GtkWidget *use_personality_computer_name_entry;
GtkWidget *use_personality_home_name_entry;
GtkWidget *use_personality_trash_name_entry;

void checkbutton_toggled_hbox1(GtkWidget *checkbutton,
		gpointer data)
{
	_checkbutton_toggled_base(checkbutton,data,desktop_hbox1);
}

void checkbutton_toggled_hbox2(GtkWidget *checkbutton,
		gpointer data)
{
	_checkbutton_toggled_base(checkbutton,data,desktop_hbox2);
}
void checkbutton_toggled_hbox3(GtkWidget *checkbutton,
		gpointer data)
{
	_checkbutton_toggled_base(checkbutton,data,desktop_hbox3);
}
void checkbutton_toggled_hbox4(GtkWidget *checkbutton,
		gpointer data)
{
	_checkbutton_toggled_base(checkbutton,data,desktop_hbox4);
}

void checkbutton_toggled_computer(GtkWidget *checkbutton,
		gpointer data)
{
	_checkbutton_toggled_entry(checkbutton,data,use_personality_computer_name_entry);
}

void checkbutton_toggled_home(GtkWidget *checkbutton,
		gpointer data)
{
	_checkbutton_toggled_entry(checkbutton,data,use_personality_home_name_entry);
}
void checkbutton_toggled_trash(GtkWidget *checkbutton,
		gpointer data)
{
	_checkbutton_toggled_entry(checkbutton,data,use_personality_trash_name_entry);
}
void entry_activated_computer(GtkWidget *entry,
		gpointer data)
{
	_entry_activated(entry,data,computer_icon_name);
}
void entry_activated_home(GtkWidget *entry,
		gpointer data)
{
	_entry_activated(entry,data,home_icon_name);
}
void entry_activated_trash(GtkWidget *entry,
		gpointer data)
{
	_entry_activated(entry,data,trash_icon_name);
}
GtkWidget *create_desktop_page()
{
	GtkWidget *desktop_main_vbox;
	GtkWidget *desktop_label;
	GtkWidget *use_nautilus_checkbutton;
	GtkWidget *show_computer_checkbutton;
	GtkWidget *desktop_vbox1;
	GtkWidget *desktop_vbox2;
	GtkWidget *desktop_vbox3;
	GtkWidget *desktop_vbox4;
	GtkWidget *desktop_hbox1_blank;
	GtkWidget *use_personality_computer_name_label;

	GtkWidget *show_home_checkbutton;
	GtkWidget *use_personality_home_name_label;

	GtkWidget *show_network_checkbutton;
	GtkWidget *show_volumes_checkbutton;
	GtkWidget *show_trash_checkbutton;
	GtkWidget *use_personality_trash_name_checkbutton;

	GtkWidget *use_home_as_desktop_checkbutton;

	desktop_main_vbox=gtk_vbox_new(FALSE,5);
	gtk_widget_show(desktop_main_vbox);
	gtk_container_set_border_width(GTK_CONTAINER(desktop_main_vbox),5);

	desktop_label=gtk_label_new(NULL);
	gtk_label_set_markup(GTK_LABEL(desktop_label),_("<b>Desktop Icon settings</b>"));
	gtk_misc_set_alignment(GTK_MISC(desktop_label),0,0);
	gtk_widget_show(desktop_label);
	gtk_box_pack_start(GTK_BOX(desktop_main_vbox),desktop_label,FALSE,FALSE,0);

	use_nautilus_checkbutton=create_gconf_checkbutton(_("Show desktop icons"),show_desktop,nautilus_preferences_dir,checkbutton_toggled_hbox1,NULL);
	gtk_widget_show(use_nautilus_checkbutton);
	gtk_box_pack_start(GTK_BOX(desktop_main_vbox),use_nautilus_checkbutton,FALSE,FALSE,0);

	desktop_hbox1=gtk_hbox_new(FALSE,10);
	gtk_widget_show(desktop_hbox1);
	gtk_box_pack_start(GTK_BOX(desktop_main_vbox),desktop_hbox1,FALSE,FALSE,0);
	
	desktop_hbox1_blank=gtk_label_new(" ");
	gtk_widget_show(desktop_hbox1_blank);
	gtk_box_pack_start(GTK_BOX(desktop_hbox1),desktop_hbox1_blank,FALSE,FALSE,0);

	desktop_vbox1=gtk_vbox_new(FALSE,5);
	gtk_widget_show(desktop_vbox1);
	gtk_box_pack_start(GTK_BOX(desktop_hbox1),desktop_vbox1,FALSE,FALSE,0);

	if(gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(use_nautilus_checkbutton))==FALSE){
		gtk_widget_set_sensitive(desktop_hbox1,FALSE);
	}
/*Show computer icon*/
	show_computer_checkbutton=create_gconf_checkbutton(_("Show \"Computer\" icon on desktop"),computer_icon_visible,nautilus_desktop_dir,checkbutton_toggled_hbox2,NULL);
	gtk_widget_show(show_computer_checkbutton);
	gtk_box_pack_start(GTK_BOX(desktop_vbox1),show_computer_checkbutton,FALSE,FALSE,0);
	
	desktop_hbox2=gtk_hbox_new(FALSE,10);
	gtk_widget_show(desktop_hbox2);
	gtk_box_pack_start(GTK_BOX(desktop_vbox1),desktop_hbox2,TRUE,TRUE,0);
	
	GtkWidget *computer_icon_image;
	computer_icon_image=gtk_image_new_from_icon_name("gnome-fs-client",GTK_ICON_SIZE_DIALOG);
	gtk_widget_show(computer_icon_image);
	gtk_box_pack_start(GTK_BOX(desktop_hbox2),computer_icon_image,FALSE,FALSE,0);

	desktop_vbox2=gtk_vbox_new(FALSE,5);
	gtk_widget_show(desktop_vbox2);
	gtk_box_pack_start(GTK_BOX(desktop_hbox2),desktop_vbox2,FALSE,FALSE,0);

	use_personality_computer_name_label=create_gconf_checkbutton(_("Rename the \"Computer\" icon: "),computer_icon_name,nautilus_desktop_dir,checkbutton_toggled_computer,NULL);
	gtk_widget_show(use_personality_computer_name_label);
	gtk_box_pack_start(GTK_BOX(desktop_vbox2),use_personality_computer_name_label,FALSE,FALSE,0);
	
	use_personality_computer_name_entry=create_gconf_entry(computer_icon_name,nautilus_desktop_dir,entry_activated_computer);

	gtk_widget_show(use_personality_computer_name_entry);
	gtk_box_pack_start(GTK_BOX(desktop_vbox2),use_personality_computer_name_entry,FALSE,FALSE,0);

	
	if(gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(use_personality_computer_name_label))==FALSE){
		gtk_widget_set_sensitive(use_personality_computer_name_entry,FALSE);
	}

	if(gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(show_computer_checkbutton))==FALSE){
		gtk_widget_set_sensitive(desktop_hbox2,FALSE);
	}

/*Show HOME*/
	show_home_checkbutton=create_gconf_checkbutton(_("Show \"Home\" icon on desktop"),home_icon_visible,nautilus_desktop_dir,checkbutton_toggled_hbox3,NULL);
	gtk_widget_show(show_home_checkbutton);
	gtk_box_pack_start(GTK_BOX(desktop_vbox1),show_home_checkbutton,FALSE,FALSE,0);
	
	desktop_hbox3=gtk_hbox_new(FALSE,10);
	gtk_widget_show(desktop_hbox3);
	gtk_box_pack_start(GTK_BOX(desktop_vbox1),desktop_hbox3,FALSE,FALSE,0);

	GtkWidget *home_icon_image;
	home_icon_image=gtk_image_new_from_icon_name("gnome-fs-home",GTK_ICON_SIZE_DIALOG);
	gtk_widget_show(home_icon_image);
	gtk_box_pack_start(GTK_BOX(desktop_hbox3),home_icon_image,FALSE,FALSE,0);
	
	desktop_vbox3=gtk_vbox_new(FALSE,5);
	gtk_widget_show(desktop_vbox3);
	gtk_box_pack_start(GTK_BOX(desktop_hbox3),desktop_vbox3,FALSE,FALSE,0);

	use_personality_home_name_label=create_gconf_checkbutton(_("Rename the \"Home\" icon: "),home_icon_name,nautilus_desktop_dir,checkbutton_toggled_home,NULL);
	gtk_widget_show(use_personality_home_name_label);
	gtk_box_pack_start(GTK_BOX(desktop_vbox3),use_personality_home_name_label,FALSE,FALSE,0);

	use_personality_home_name_entry=create_gconf_entry(home_icon_name,nautilus_desktop_dir,entry_activated_home);
	gtk_widget_show(use_personality_home_name_entry);
	gtk_box_pack_start(GTK_BOX(desktop_vbox3),use_personality_home_name_entry,FALSE,FALSE,0);

	if(gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(use_personality_home_name_label))==FALSE){
		gtk_widget_set_sensitive(use_personality_home_name_entry,FALSE);
	}

	if(gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(show_home_checkbutton))==FALSE){
		gtk_widget_set_sensitive(desktop_hbox3,FALSE);
	}

/*Show Trash*/
	show_trash_checkbutton=create_gconf_checkbutton(_("Show \"Trash\" icon on desktop"),trash_icon_visible,nautilus_desktop_dir,checkbutton_toggled_hbox4,NULL);
	gtk_widget_show(show_trash_checkbutton);
	gtk_box_pack_start(GTK_BOX(desktop_vbox1),show_trash_checkbutton,FALSE,FALSE,0);
	
	desktop_hbox4=gtk_hbox_new(FALSE,10);
	gtk_widget_show(desktop_hbox4);
	gtk_box_pack_start(GTK_BOX(desktop_vbox1),desktop_hbox4,FALSE,FALSE,0);

	GtkWidget *trash_icon_image;
	trash_icon_image=gtk_image_new_from_icon_name("gnome-fs-trash-empty",GTK_ICON_SIZE_DIALOG);
	gtk_widget_show(trash_icon_image);
	gtk_box_pack_start(GTK_BOX(desktop_hbox4),trash_icon_image,FALSE,FALSE,0);
	
	desktop_vbox4=gtk_vbox_new(FALSE,5);
	gtk_widget_show(desktop_vbox4);
	gtk_box_pack_start(GTK_BOX(desktop_hbox4),desktop_vbox4,FALSE,FALSE,0);

	use_personality_trash_name_checkbutton=create_gconf_checkbutton(_("Rename the \"Trash\" icon: "),trash_icon_name,nautilus_desktop_dir,checkbutton_toggled_trash,NULL);
	gtk_widget_show(use_personality_trash_name_checkbutton);
	gtk_box_pack_start(GTK_BOX(desktop_vbox4),use_personality_trash_name_checkbutton,FALSE,FALSE,0);

	use_personality_trash_name_entry=create_gconf_entry(trash_icon_name,nautilus_desktop_dir,entry_activated_trash);
	gtk_widget_show(use_personality_trash_name_entry);
	gtk_box_pack_start(GTK_BOX(desktop_vbox4),use_personality_trash_name_entry,FALSE,FALSE,0);

	if(gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(use_personality_trash_name_checkbutton))==FALSE){
		gtk_widget_set_sensitive(use_personality_trash_name_entry,FALSE);
	}

	if(gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(show_trash_checkbutton))==FALSE){
		gtk_widget_set_sensitive(desktop_hbox4,FALSE);
	}

/*Other*/
	use_home_as_desktop_checkbutton=create_gconf_checkbutton(_("Use Home Directory as Desktop"),use_home_as_desktop,nautilus_preferences_dir,checkbutton_toggled,NULL);
	gtk_widget_show(use_home_as_desktop_checkbutton);
	gtk_box_pack_start(GTK_BOX(desktop_vbox1),use_home_as_desktop_checkbutton,FALSE,FALSE,0);

	show_network_checkbutton=create_gconf_checkbutton(_("Show \"Network\" icon on desktop"),network_icon_visible,nautilus_desktop_dir,checkbutton_toggled,NULL);
	gtk_widget_show(show_network_checkbutton);
	gtk_box_pack_start(GTK_BOX(desktop_vbox1),show_network_checkbutton,FALSE,FALSE,0);

	show_volumes_checkbutton=create_gconf_checkbutton(_("Show Mounted Volumes on desktop"),volumes_visible,nautilus_desktop_dir,checkbutton_toggled,NULL);
	gtk_widget_show(show_volumes_checkbutton);
	gtk_box_pack_start(GTK_BOX(desktop_vbox1),show_volumes_checkbutton,FALSE,FALSE,0);

	return desktop_main_vbox;
}
