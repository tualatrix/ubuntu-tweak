#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"
#include "desktop_page.h"
#include "system_page.h"

GtkWidget *create_personality_notebook()
{
/*定义笔记本*/
	GtkWidget *notebook;
	GtkWidget *desktop_main_vbox;
	GtkWidget *system_main_vbox;
	GtkWidget *history_main_vbox;
	GtkWidget *desktop_page_label;

	notebook=gtk_notebook_new();
	gtk_notebook_set_tab_pos(GTK_NOTEBOOK(notebook),GTK_POS_TOP);

	desktop_main_vbox=create_desktop_page();
	system_main_vbox=create_system_page();

/*桌面的大标签*/
	desktop_page_label=gtk_label_new("桌面图标");
	gtk_widget_show(desktop_page_label);

	GtkWidget *frame2;
	GtkWidget *frame3;
	GtkWidget *history_page_label;
	GtkWidget *checkbutton1;

	checkbutton1=gtk_check_button_new_with_mnemonic("checkbutton1");
	gtk_widget_show(checkbutton1);


	GtkWidget *system_page_label;
	system_page_label=gtk_label_new("系统选项");
	gtk_widget_show(system_page_label);


	frame3=gtk_frame_new("frame 3");
	gtk_widget_show(frame3);

	history_page_label=gtk_label_new("历史记录");
	gtk_widget_show(history_page_label);

	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),desktop_main_vbox,desktop_page_label);

	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),system_main_vbox,system_page_label);
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),frame3,history_page_label);

	return notebook;
}
