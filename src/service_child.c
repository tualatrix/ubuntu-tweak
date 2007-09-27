#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"
#include <gdk/gdkx.h>

int main(int argc, char *argv[])
{
	guint64 xid;

	GtkWidget *window;
	GtkWidget *label;

	gtk_init(&argc, &argv);

	if(argc<2){
		g_print("Usage: service-child WINDOW_ID\n");
		return 1;
	}

	xid=g_ascii_strtoull(argv[1],NULL,0);
	//g_print("WINDOW_ID is '%d'\n",xid);

	if(xid==0){
		g_print("Invalid window id '%s'\n", argv[1]);
		return 1;
	}

	window=gtk_plug_new(xid);

	gtk_signal_connect(GTK_OBJECT(window),"destroy",
		     GTK_SIGNAL_FUNC(gtk_main_quit), NULL);

	gtk_container_border_width(GTK_CONTAINER(window), 0);

	label=gtk_label_new(NULL);
	gtk_label_set_markup(GTK_LABEL(label),_("<b>Welcome:</b>\nWelcome to use service-page."));
	gtk_widget_show(label);
	gtk_container_add(GTK_CONTAINER(window),label);

	gtk_widget_show(window);

	gtk_main();

	return 0;
}
