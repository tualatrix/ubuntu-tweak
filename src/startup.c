#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"
#include "session_page.h"

/*
create the startup notebook for related options
*/
GtkWidget *create_startup_notebook()
{
	GtkWidget *notebook;
	GtkWidget *session_main_vbox;
	GtkWidget *session_page_label;

	notebook=gtk_notebook_new();
	gtk_notebook_set_tab_pos(GTK_NOTEBOOK(notebook),GTK_POS_TOP);

/*Session page*/
	session_main_vbox=create_session_page();
	session_page_label=gtk_label_new(_("Session"));
	gtk_widget_show(session_page_label);
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),session_main_vbox,session_page_label);

	return notebook;
}
