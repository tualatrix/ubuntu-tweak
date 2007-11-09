#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"

/*expert mode*/
static GtkWidget *expander_gnome;
static GtkWidget *expert_label_gnome;
static GtkWidget *expert_box_gnome;
static GtkWidget *expert_animations;
static GtkWidget *expert_lockdownpanel;
static GtkWidget *expert_inputunicode;
static gpointer present_expert_gnome;

#define enable_animations_panel		"/apps/panel/global/enable_animations"
#define enable_animations_gnome		"/desktop/gnome/interface/enable_animations"
#define key_locked_down_panel		"/apps/panel/global/locked_down"
#define key_show_input_method_menu	"/desktop/gnome/interface/show_input_method_menu"
#define key_show_unicode_menu		"/desktop/gnome/interface/show_unicode_menu"
#define dir_gnome_interface		"/desktop/gnome/interface"
#define dir_panel_global		"/apps/panel/global"

static void show_expert_label_gnome()
{
	if(present_expert_gnome!=NULL){
		gtk_widget_hide(present_expert_gnome);
	}
	expert_label_gnome=nt_expert_content_new_with_string(_("Within this menu are advanced GNOME settings. If you require more information about a specific option, move your cursor over that option, and a description will appear here."));
	gtk_widget_show(expert_label_gnome);
	present_expert_gnome=expert_label_gnome;
	gtk_box_pack_start(GTK_BOX(expert_box_gnome),expert_label_gnome,TRUE,TRUE,0);
}

static void expander_change_gnome(GtkWidget *widget,gpointer data)
{
	gboolean bool;
	bool=gtk_expander_get_expanded(GTK_EXPANDER(widget));	
	if(bool==FALSE){
		show_expert_label_gnome();
	}
}

static void show_expert_animations(GtkWidget *widget,gpointer data)
{
	if(present_expert_gnome!=expert_animations){
		gtk_widget_hide(present_expert_gnome);
		expert_animations=nt_expert_content_new_with_string(_("It seems that if you disable this option, GNOME will appear quicker."));
		gtk_widget_show(expert_animations);
		present_expert_gnome=expert_animations;
		gtk_box_pack_start(GTK_BOX(expert_box_gnome),expert_animations,FALSE,FALSE,0);
	}
}

static void show_expert_lockdownpanel(GtkWidget *widget,gpointer data)
{
	if(present_expert_gnome!=expert_lockdownpanel){
		gtk_widget_hide(present_expert_gnome);
		expert_lockdownpanel=nt_expert_content_new_with_string(_("Check this button if you do not wish your gnome-panel to be changed."));
		gtk_widget_show(expert_lockdownpanel);
		present_expert_gnome=expert_lockdownpanel;
		gtk_box_pack_start(GTK_BOX(expert_box_gnome),expert_lockdownpanel,FALSE,FALSE,0);
	}
}

static void show_expert_inputunicode(GtkWidget *widget,gpointer data)
{
	if(present_expert_gnome!=expert_inputunicode){
		gtk_widget_hide(present_expert_gnome);
		expert_inputunicode=nt_expert_content_new_with_string(_("Right-clicking in an editable area (such as Text Editor) will allow you to select your Input Method. This option is useful if you need to type in a different language, such as Cyrillic or Thai-Lao. This option enables or disables the Input Method selection."));
		gtk_widget_show(expert_inputunicode);
		present_expert_gnome=expert_inputunicode;
		gtk_box_pack_start(GTK_BOX(expert_box_gnome),expert_inputunicode,FALSE,FALSE,0);
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

	checkbutton=ut_checkbutton_new_with_gconf(_("Enable GNOME Animations Panel"),enable_animations_panel,dir_panel_global,ut_checkbutton_toggled,show_expert_animations);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);

	checkbutton=ut_checkbutton_new_with_gconf(_("Enable GNOME Animations Effect"),enable_animations_gnome,dir_gnome_interface,ut_checkbutton_toggled,show_expert_animations);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);

	checkbutton=ut_checkbutton_new_with_gconf(_("Complete lockdown of the Panel "),key_locked_down_panel,dir_panel_global,ut_checkbutton_toggled,show_expert_lockdownpanel);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);

	checkbutton=ut_checkbutton_new_with_gconf(_("Show Input Method menu in the right-click"),key_show_input_method_menu,dir_gnome_interface,ut_checkbutton_toggled,show_expert_inputunicode);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);	

	checkbutton=ut_checkbutton_new_with_gconf(_("Show Unicode Method menu in the right-click"),key_show_unicode_menu,dir_gnome_interface,ut_checkbutton_toggled,show_expert_inputunicode);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);	

/*expander*/
	expander_gnome=gtk_expander_new_with_mnemonic(_("Need some help? Click here!"));
	gtk_widget_show(expander_gnome);
	g_signal_connect(G_OBJECT(expander_gnome),"activate",G_CALLBACK(expander_change_gnome),NULL);
	gtk_box_pack_end(GTK_BOX(main_vbox),expander_gnome,FALSE,FALSE,0);

	expert_box_gnome=gtk_vbox_new(FALSE,0);
	gtk_widget_set_size_request(GTK_WIDGET(expert_box_gnome),200,100);
	gtk_widget_show(expert_box_gnome);
	gtk_container_add(GTK_CONTAINER(expander_gnome),expert_box_gnome);

	return main_vbox; 
}
