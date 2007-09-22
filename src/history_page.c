#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"

GtkWidget *checkbutton_runapplication;
GtkWidget *checkbutton_searchfiles;
GtkWidget *checkbutton_gconfeditor;

void sweep_history(GtkWidget *widget,gpointer data)
{
	GConfClient *client;
	GtkMessageDialog *dialog;
	
	client=gconf_client_get_default();

	if(gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(checkbutton_runapplication))||gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(checkbutton_searchfiles))||gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(checkbutton_gconfeditor))){
		if(gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(checkbutton_runapplication))){
			gconf_client_set_list(client,"/apps/gnome-settings/gnome-panel/history-gnome-run",GCONF_VALUE_STRING,NULL,NULL);
			gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton_runapplication),FALSE);
		}
		if(gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(checkbutton_searchfiles))){
			gconf_client_set_list(client,"/apps/gconf-editor/recents",GCONF_VALUE_STRING,NULL,NULL);
			gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton_searchfiles),FALSE);
		}
		if(gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(checkbutton_gconfeditor))){
			gconf_client_set_list(client,"/apps/gnome-settings/gnome-search-tool/history-gsearchtool-file-entry",GCONF_VALUE_STRING,NULL,NULL);
			gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton_gconfeditor),FALSE);
		}
		dialog=gtk_message_dialog_new(window,
					GTK_DIALOG_DESTROY_WITH_PARENT,
					GTK_MESSAGE_INFO,
					GTK_BUTTONS_OK,
					_("Yeah!\nThe history that you selected is cleaned up!"),NULL
					);
		gtk_dialog_run(GTK_MESSAGE_DIALOG(dialog));
		gtk_widget_destroy(dialog);
	}else{
		dialog=gtk_message_dialog_new(window,
					GTK_DIALOG_DESTROY_WITH_PARENT,
					GTK_MESSAGE_QUESTION,
					GTK_BUTTONS_OK,
					_("It seems that you don't select anything, why you clicked me?"),NULL
					);
		gtk_dialog_run(GTK_MESSAGE_DIALOG(dialog));
		gtk_widget_destroy(dialog);
	}
}

GtkWidget *create_history_page()
{
	GtkWidget *main_vbox;
	GtkWidget *vbox;
	GtkWidget *hbox;
	GtkWidget *label;

	main_vbox=gtk_vbox_new(FALSE,5);
	gtk_widget_show(main_vbox);
	gtk_container_set_border_width(GTK_CONTAINER(main_vbox),5);

	label=gtk_label_new(NULL);
	gtk_label_set_markup(GTK_LABEL(label),_("<b>Cleaning history</b>"));
	gtk_misc_set_alignment(GTK_MISC(label),0,0);
	gtk_widget_show(label);
	gtk_box_pack_start(GTK_BOX(main_vbox),label,FALSE,FALSE,0);

	GtkWidget *frame;
	frame=gtk_frame_new(_("CD Burner"));
	gtk_widget_show(frame);
	gtk_box_pack_start(GTK_BOX(main_vbox),frame,FALSE,FALSE,0);

	vbox=gtk_vbox_new(FALSE,5);
	gtk_widget_show(vbox);
	gtk_container_add(GTK_CONTAINER(frame),vbox);

	checkbutton_runapplication=gtk_check_button_new_with_label(_("Clean \"Run Application\" history"));
	gtk_widget_show(checkbutton_runapplication);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton_runapplication,FALSE,FALSE,0);

	checkbutton_searchfiles=gtk_check_button_new_with_label(_("Clean \"Search Files\" history"));
	gtk_widget_show(checkbutton_searchfiles);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton_searchfiles,FALSE,FALSE,0);

	checkbutton_gconfeditor=gtk_check_button_new_with_label(_("Clean \"Gconf-editor\" history"));
	gtk_widget_show(checkbutton_gconfeditor);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton_gconfeditor,FALSE,FALSE,0);

	hbox=gtk_hbox_new(FALSE,0);
	gtk_widget_show(hbox);
	gtk_box_pack_start(GTK_BOX(main_vbox),hbox,FALSE,FALSE,0);

	GtkWidget *button;
	button=gtk_button_new_with_label(_("Clean Now"));
	g_signal_connect(G_OBJECT(button),"clicked",G_CALLBACK(sweep_history),NULL);
	gtk_widget_show(button);
	gtk_box_pack_end(GTK_BOX(hbox),button,FALSE,FALSE,0);

	return main_vbox; 
}
