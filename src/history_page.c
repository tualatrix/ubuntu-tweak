#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"

GtkWidget *checkbutton_runapplication;
GtkWidget *checkbutton_searchfiles;

void sweep_history(GtkWidget *widget,gpointer data)
{
	GConfClient *client;
	GtkMessageDialog *dialog;
	
	client=gconf_client_get_default();

	if(gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(checkbutton_runapplication))){
		if(gconf_client_set_list(client,"/apps/gnome-settings/gnome-panel/history-gnome-run",GCONF_VALUE_STRING,NULL,NULL)){
			dialog=gtk_message_dialog_new(window,
						GTK_DIALOG_DESTROY_WITH_PARENT,
						GTK_MESSAGE_INFO,
						GTK_BUTTONS_OK,
						"Hello,You are fool","haha"
						);
			gtk_dialog_run(GTK_MESSAGE_DIALOG(dialog));
			gtk_widget_destroy(dialog);
			gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton_runapplication),FALSE);
		};
	}
}

GtkWidget *create_history_page()
{
	GtkWidget *main_vbox;
	GtkWidget *vbox;
	GtkWidget *hbox;
	GtkWidget *label;

	main_vbox=gtk_vbox_new(FALSE,10);
	gtk_widget_show(main_vbox);
	gtk_container_set_border_width(GTK_CONTAINER(main_vbox),5);

	label=gtk_label_new(_("Clean history"));
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

	checkbutton_runapplication=gtk_check_button_new_with_label(_("Sweep \"Run Application\" history"));
	gtk_widget_show(checkbutton_runapplication);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton_runapplication,FALSE,FALSE,0);

	checkbutton_searchfiles=gtk_check_button_new_with_label(_("Sweep \"Search Files\" history"));
	gtk_widget_show(checkbutton_searchfiles);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton_searchfiles,FALSE,FALSE,0);

	hbox=gtk_hbox_new(FALSE,0);
	gtk_widget_show(hbox);
	gtk_box_pack_start(GTK_BOX(vbox),hbox,FALSE,FALSE,0);

	GtkWidget *button;
	button=gtk_button_new_with_label(_("Sweep"));
	g_signal_connect(G_OBJECT(button),"clicked",G_CALLBACK(sweep_history),NULL);
	gtk_widget_show(button);
	gtk_box_pack_end(GTK_BOX(hbox),button,FALSE,FALSE,0);

	return main_vbox; 
}
