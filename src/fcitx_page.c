#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"

gchar *key_fcitx_table[9]={
	"/apps/ubuntu-tweak/user/fcitx/cj",
	"/apps/ubuntu-tweak/user/fcitx/erbi",
	"/apps/ubuntu-tweak/user/fcitx/py",
	"/apps/ubuntu-tweak/user/fcitx/qw",
	"/apps/ubuntu-tweak/user/fcitx/qxm",
	"/apps/ubuntu-tweak/user/fcitx/sp",
	"/apps/ubuntu-tweak/user/fcitx/wbpy",
	"/apps/ubuntu-tweak/user/fcitx/wbx",
	"/apps/ubuntu-tweak/user/fcitx/wf",	
};

GtkWidget *create_fcitx_page()
{
	GtkWidget *main_vbox;
	GtkWidget *vbox;
	GtkWidget *hbox;
	GtkWidget *label;
	GtkWidget *separator;
	GtkWidget *checkbutton;

	main_vbox=gtk_vbox_new(FALSE,10);
	gtk_widget_show(main_vbox);
	gtk_container_set_border_width(GTK_CONTAINER(main_vbox),10);


	label=gtk_label_new(_("Fcitx"));
	gtk_misc_set_alignment(GTK_MISC(label),0,0);
	gtk_widget_show(label);
	gtk_box_pack_start(GTK_BOX(main_vbox),label,FALSE,FALSE,0);

	hbox=gtk_hbox_new(FALSE,5);
	gtk_widget_show(hbox);
	gtk_box_pack_start(GTK_BOX(main_vbox),hbox,FALSE,FALSE,0);

	label=gtk_label_new(" ");
	gtk_widget_show(label);
	gtk_box_pack_start(GTK_BOX(hbox),label,FALSE,FALSE,0);


	checkbutton=create_text_checkbutton("启用仓颉",key_fcitx_table[0],NULL,NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("启用二笔",key_fcitx_table[1],NULL,NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("启用拼音",key_fcitx_table[2],NULL,NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("启用区位",key_fcitx_table[3],NULL,NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	hbox=gtk_hbox_new(FALSE,5);
	gtk_widget_show(hbox);
	gtk_box_pack_start(GTK_BOX(main_vbox),hbox,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("启用冰蟾全息",key_fcitx_table[4],NULL,NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("启用双拼",key_fcitx_table[5],NULL,NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("启用五笔拼音",key_fcitx_table[6],NULL,NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("启用五笔",key_fcitx_table[7],NULL,NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("启用晚风",key_fcitx_table[8],NULL,NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	vbox=gtk_vbox_new(FALSE,10);
	gtk_widget_show(vbox);
	gtk_box_pack_start(GTK_BOX(hbox),vbox,FALSE,FALSE,0);

	return main_vbox; 
}
