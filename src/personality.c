#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"
#include "desktop_page.h"
#include "nautilus_page.h"

GtkWidget *create_personality_notebook()
{
/*定义笔记本*/
	GtkWidget *notebook;
	GtkWidget *main_vbox;
	GtkWidget *page_label;

	notebook=gtk_notebook_new();
	gtk_notebook_set_tab_pos(GTK_NOTEBOOK(notebook),GTK_POS_TOP);

/*Desktop label*/
	main_vbox=create_desktop_page();
	page_label=gtk_label_new(_("Desktop Icon"));
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),main_vbox,page_label);

	main_vbox=create_nautilus_page();
	page_label=gtk_label_new(_("Nautilus"));
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),main_vbox,page_label);

	main_vbox=gtk_frame_new(_("Not complete yet"));
	gtk_widget_show(main_vbox);
	page_label=gtk_label_new(_("History"));
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),main_vbox,page_label);

	return notebook;
}
