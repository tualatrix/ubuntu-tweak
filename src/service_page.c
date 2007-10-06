#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "stdlib.h"
#include "ubuntu-tweak.h"
#include <gdk/gdkx.h>

gchar *insert_shell[3];
GPid pid;
GPid *pid_pointer=&pid;

GtkWidget *socket = 0;
GtkWidget *main_vbox;

static void insert_service_child(GtkWidget *widget, gpointer data);

GtkWidget *create_service_page()
{
	GtkWidget *vbox;
	GtkWidget *hbox;
	GtkWidget *label;
	GtkWidget *button;

	main_vbox=gtk_vbox_new(FALSE,10);
	gtk_widget_set_size_request(GTK_WIDGET(main_vbox),200,100);
	gtk_widget_show(main_vbox);
	gtk_container_set_border_width(GTK_CONTAINER(main_vbox),5);

	label=gtk_label_new(NULL);
	gtk_label_set_markup(GTK_LABEL(label),_("<b>Manage Services in your system</b>"));
	gtk_misc_set_alignment(GTK_MISC(label),0,0);
	gtk_widget_show(label);
	gtk_box_pack_start(GTK_BOX(main_vbox),label,FALSE,FALSE,0);
	
	hbox=gtk_hbox_new(FALSE,10);
	gtk_widget_show(hbox);
	gtk_box_pack_start(GTK_BOX(main_vbox),hbox,FALSE,FALSE,0);
	
	label=gtk_label_new(NULL);
	gtk_label_set_markup(GTK_LABEL(label),_("<b>WARNING:</b> To change the following settings you need root permission.\nIf you are not the Administrator of this system, please log in with those creditials.\nAlternatively, you can run <b>gksudo ubuntu-tweak</b> from the Application Run dialog (Alt+F2)."));
	gtk_widget_show(label);
	gtk_box_pack_start(GTK_BOX(hbox),label,FALSE,FALSE,0);

	button=gtk_button_new_with_label(_("Start"));
	gtk_widget_show(button);
	gtk_box_pack_start(GTK_BOX(main_vbox),button,FALSE,FALSE,0);
	gtk_signal_connect(GTK_OBJECT(button), "clicked",GTK_SIGNAL_FUNC(insert_service_child), NULL);

	vbox=gtk_vbox_new(FALSE,0);
	gtk_widget_show(vbox);
	gtk_box_pack_start(GTK_BOX(hbox),vbox,FALSE,FALSE,0);

	return main_vbox;
}

void insert_service_child(GtkWidget *widget,gpointer data)
{
	gchar xid[20];

	if (socket)
		return;

	socket = gtk_socket_new();
	gtk_box_pack_start(GTK_BOX(main_vbox), socket, TRUE, TRUE, 0);
	gtk_widget_show(socket);

	gdk_flush();

	g_sprintf(xid, "%#lx", GDK_WINDOW_XWINDOW(socket->window));

	insert_shell[0]="gksu";
	insert_shell[1]="service-child",
	insert_shell[2]=xid;

//	g_print("the shell is: %s %s %s\n",insert_shell[0],insert_shell[1],insert_shell[2]);

	g_spawn_async	(NULL,
			insert_shell,
			NULL,
			G_SPAWN_SEARCH_PATH,
			NULL,
			NULL,
			pid_pointer,
			NULL);
}
