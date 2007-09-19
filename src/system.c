#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"
#include "powermanager_page.h"
#include "gnome_page.h"

GtkWidget *create_system_notebook()
{
	GtkWidget *notebook;
	GtkWidget *main_vbox;
	GtkWidget *label;

	notebook=gtk_notebook_new();
	gtk_notebook_set_tab_pos(GTK_NOTEBOOK(notebook),GTK_POS_TOP);

	main_vbox=create_gnome_page();
	label=gtk_label_new(_("GNOME Options"));
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),main_vbox,label);

	label=gtk_label_new(_("Advance Power Manager"));
	main_vbox=create_powermanager_page();
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),main_vbox,label);

	return notebook;
}
