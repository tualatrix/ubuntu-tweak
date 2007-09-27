#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"
#include "session_page.h"
#include "service_page.h"

/*
create the startup notebook for related options
*/
GtkWidget *create_startup_notebook()
{
	GtkWidget *notebook;
	GtkWidget *main_vbox;
	GtkWidget *label;
	GtkWidget *service_main_vbox;

	notebook=gtk_notebook_new();
	gtk_notebook_set_tab_pos(GTK_NOTEBOOK(notebook),GTK_POS_TOP);

/*Session page*/
	main_vbox=create_session_page();
	label=gtk_label_new(_("Session"));
	gtk_widget_show(label);
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),main_vbox,label);

/*Service page*/
	service_main_vbox=create_service_page();
	label=gtk_label_new(_("Service"));
	gtk_widget_show(label);
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),service_main_vbox,label);

	return notebook;
}
