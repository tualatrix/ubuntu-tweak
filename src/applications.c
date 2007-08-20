#include "ubuntu-tweak.h"
#include "desktop_page.h"
#include "mplayer_page.h"
#include <stdio.h>

gchar *ubuntu_tweak_awn="/apps/ubuntu-tweak/apps/awn";
gchar *style[]={"自定义设置",
			"Leopard现在3D样式",
			"MacOSX经典样式"};

gchar *glass_step_1="/apps/avant-window-navigator/bar/glass_step_1";
gchar *glass_step_2="/apps/avant-window-navigator/bar/glass_step_2";
gchar *icon_offset="/apps/avant-window-navigator/bar/icon_offset";
gchar *tasks_have_arrows="/apps/avant-window-navigator/app/tasks_have_arrows";
gchar *arrow_color="/apps/avant-window-navigator/app/arrow_color";
gchar *rounded_corners="/apps/avant-window-navigator/bar/rounded_corners";
gchar *hilight_color="/apps/avant-window-navigator/bar/hilight_color";
gchar *border_color="/apps/avant-window-navigator/bar/border_color";

gchar *bar_angle="/apps/avant-window-navigator/bar/bar_angle";

void set_to_classic()
{
	GConfClient *client;

	client=gconf_client_get_default();

	gconf_client_set_int(client,bar_angle,0,NULL);
	gconf_client_set_string(client,glass_step_1,"7783AFC8",NULL);
	gconf_client_set_string(client,glass_step_2,"7783AFC8",NULL);
	gconf_client_set_int(client,icon_offset,0,NULL);
	gconf_client_set_bool(client,tasks_have_arrows,TRUE,NULL);
	gconf_client_set_string(client,arrow_color,"FFFFFF66",NULL);
	gconf_client_set_bool(client,rounded_corners,FALSE,NULL);
	gconf_client_set_string(client,hilight_color,"FFFFFF00",NULL);
	gconf_client_set_string(client,border_color,"FFFFFF3C",NULL);

	gconf_client_set_int(client,ubuntu_tweak_awn,2,NULL);
}
void set_to_leopard()
{
	GConfClient *client;

	client=gconf_client_get_default();
	gconf_client_set_int(client,bar_angle,30,NULL);
	gconf_client_set_string(client,glass_step_1,"A9A9A9C8",NULL);
	gconf_client_set_string(client,glass_step_2,"A9A9A9BE",NULL);
	gconf_client_set_int(client,icon_offset,18,NULL);
	gconf_client_set_bool(client,tasks_have_arrows,TRUE,NULL);
	gconf_client_set_string(client,arrow_color,"FFFFFF66",NULL);
	gconf_client_set_bool(client,rounded_corners,FALSE,NULL);
	gconf_client_set_string(client,hilight_color,"FFFFFF00",NULL);
	gconf_client_set_string(client,border_color,"FFFFFF3C",NULL);

	gconf_client_set_int(client,ubuntu_tweak_awn,1,NULL);
}
void combobox_changed(GtkWidget *widget,gpointer data)
{
	gchar *str;
	str=gtk_combo_box_get_active_text(GTK_COMBO_BOX(widget));
	if(!strcmp(str,style[2])){
		set_to_classic();
	}
	else if(!strcmp(str,style[1])){
		set_to_leopard();
	}
	else{
	}
}


GtkWidget *create_awn_page()
{
	GtkWidget *main_vbox;
	GtkWidget *vbox;
	GtkWidget *hbox;
	GtkWidget *label;
	GtkWidget *checkbutton;
	GtkWidget *button;
	GtkWidget *combobox;
	GConfClient *client;

	main_vbox=gtk_vbox_new(FALSE,10);
	gtk_widget_show(main_vbox);
	gtk_container_set_border_width(GTK_CONTAINER(main_vbox),5);

	label=gtk_label_new(_("Here, You can easily choose or configure Avant Window Navigator to your style"));
	gtk_misc_set_alignment(GTK_MISC(label),0,0);
	gtk_widget_show(label);
	gtk_box_pack_start(GTK_BOX(main_vbox),label,FALSE,FALSE,0);

	hbox=gtk_hbox_new(FALSE,0);
	gtk_widget_show(hbox);
	gtk_box_pack_start(GTK_BOX(main_vbox),hbox,FALSE,FALSE,0);

	label=gtk_label_new("Choose the AWN Style:");
	gtk_widget_show(label);
	gtk_box_pack_start(GTK_BOX(hbox),label,FALSE,FALSE,0);

	combobox=gtk_combo_box_new_text();
	gtk_widget_show(combobox);
	g_signal_connect(G_OBJECT(combobox),"changed",G_CALLBACK(combobox_changed),NULL);
	gtk_box_pack_start(GTK_BOX(hbox),combobox,FALSE,FALSE,0);

	gtk_combo_box_append_text(GTK_COMBO_BOX(combobox),style[0]);
	gtk_combo_box_append_text(GTK_COMBO_BOX(combobox),style[1]);
	gtk_combo_box_append_text(GTK_COMBO_BOX(combobox),style[2]);
	
	client=gconf_client_get_default();
	if(gconf_client_get_int(client,ubuntu_tweak_awn,NULL)==1){
		gtk_combo_box_set_active(GTK_COMBO_BOX(combobox),1);
	}else if(gconf_client_get_int(client,ubuntu_tweak_awn,NULL)==2){
		gtk_combo_box_set_active(GTK_COMBO_BOX(combobox),2);
	}else{
		gtk_combo_box_set_active(GTK_COMBO_BOX(combobox),0);
	}
	vbox=gtk_vbox_new(FALSE,0);
	gtk_widget_show(vbox);
	gtk_box_pack_start(GTK_BOX(main_vbox),vbox,FALSE,FALSE,0);

	return main_vbox;
}

GtkWidget *create_applications_notebook()
{
	GtkWidget *notebook;
	GtkWidget *main_vbox;
	GtkWidget *page_label;

	notebook=gtk_notebook_new();
	gtk_notebook_set_tab_pos(GTK_NOTEBOOK(notebook),GTK_POS_TOP);

	main_vbox=create_awn_page();
	gtk_widget_show(main_vbox);
	page_label=gtk_label_new("Avant Window Navigator");
	gtk_widget_show(page_label);
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),main_vbox,page_label);	
	
	main_vbox=create_mplayer_page();
	gtk_widget_show(main_vbox);
	page_label=gtk_label_new("mplayer");
	gtk_widget_show(page_label);
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),main_vbox,page_label);	
	
	return notebook;
}

