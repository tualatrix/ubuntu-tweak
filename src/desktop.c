#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"
#include "desktop_page.h"
#include "nautilus_page.h"
#include "history_page.h"
#include "gnome_page.h"

GtkWidget *create_desktop_notebook()
{
/*定义笔记本*/
	GtkWidget *notebook;
	GtkWidget *main_vbox;
	GtkWidget *label;

	notebook=gtk_notebook_new();
	gtk_notebook_set_tab_pos(GTK_NOTEBOOK(notebook),GTK_POS_TOP);

/*Desktop label*/
	main_vbox=create_desktop_page();
	label=gtk_label_new(_("Desktop Icon"));
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),main_vbox,label);

	main_vbox=create_gnome_page();
	label=gtk_label_new(_("GNOME Options"));
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),main_vbox,label);

	main_vbox=create_nautilus_page();
	label=gtk_label_new(_("Nautilus"));
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),main_vbox,label);

	main_vbox=create_history_page();
	gtk_widget_show(main_vbox);
	label=gtk_label_new(_("History"));
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),main_vbox,label);

	return notebook;
}
