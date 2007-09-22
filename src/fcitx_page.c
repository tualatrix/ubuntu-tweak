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
gchar *key_fcitx_apperance[3]={
	"/apps/ubuntu-tweak/user/fcitx/banner_mode",
	"/apps/ubuntu-tweak/user/fcitx/show_type_speed",
	"/apps/ubuntu-tweak/user/fcitx/show_version",
};
gchar *script_fcitx=PACKAGE_SCRIPTS_DIR"/ubuntu-tweak-fcitx";

GtkWidget *create_fcitx_page()
{
	GtkWidget *main_vbox;
	GtkWidget *vbox;
	GtkWidget *hbox;
	GtkWidget *frame;
	GtkWidget *label;
	GtkWidget *checkbutton;

	main_vbox=gtk_vbox_new(FALSE,10);
	gtk_widget_show(main_vbox);
	gtk_container_set_border_width(GTK_CONTAINER(main_vbox),10);

	label=gtk_label_new(NULL);
	gtk_label_set_markup(GTK_LABEL(label),_("<b>欢迎使用Fcitx输入法设置！</b>\n在这里，你可以禁用掉一些你并不使用的码表；\n或进行一些有关输入法行为的设置。\n未来会提供更棒的设置。"));
	gtk_misc_set_alignment(GTK_MISC(label),0,0);
	gtk_widget_show(label);
	gtk_box_pack_start(GTK_BOX(main_vbox),label,FALSE,FALSE,0);

	frame=gtk_frame_new("输入法");
	gtk_widget_show(frame);
	gtk_box_pack_start(GTK_BOX(main_vbox),frame,FALSE,FALSE,0);

	vbox=gtk_vbox_new(FALSE,10);
	gtk_widget_show(vbox);
	gtk_container_add(GTK_CONTAINER(frame),vbox);

	hbox=gtk_hbox_new(FALSE,5);
	gtk_widget_show(hbox);
	gtk_box_pack_start(GTK_BOX(vbox),hbox,FALSE,FALSE,0);
	
	checkbutton=create_text_checkbutton("启用仓颉",key_fcitx_table[0],g_strconcat(script_fcitx," cj",NULL),NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("启用二笔",key_fcitx_table[1],g_strconcat(script_fcitx," erbi",NULL),NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("启用拼音",key_fcitx_table[2],g_strconcat(script_fcitx," py",NULL),NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("启用双拼",key_fcitx_table[5],g_strconcat(script_fcitx," sp",NULL),NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("启用区位",key_fcitx_table[3],g_strconcat(script_fcitx," qw",NULL),NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	hbox=gtk_hbox_new(FALSE,5);
	gtk_widget_show(hbox);
	gtk_box_pack_start(GTK_BOX(vbox),hbox,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("启用冰蟾全息",key_fcitx_table[4],g_strconcat(script_fcitx," qxm",NULL),NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("启用五笔拼音",key_fcitx_table[6],g_strconcat(script_fcitx," wbpy",NULL),NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("启用五笔",key_fcitx_table[7],g_strconcat(script_fcitx," wbx",NULL),NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("启用晚风",key_fcitx_table[8],g_strconcat(script_fcitx," wf",NULL),NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	vbox=gtk_vbox_new(FALSE,10);
	gtk_widget_show(vbox);
	gtk_box_pack_start(GTK_BOX(hbox),vbox,FALSE,FALSE,0);

	frame=gtk_frame_new("界面");
	gtk_widget_show(frame);
	gtk_box_pack_start(GTK_BOX(main_vbox),frame,FALSE,FALSE,0);

	vbox=gtk_vbox_new(FALSE,10);
	gtk_widget_show(vbox);
	gtk_container_add(GTK_CONTAINER(frame),vbox);

	hbox=gtk_hbox_new(FALSE,10);
	gtk_widget_show(hbox);
	gtk_box_pack_start(GTK_BOX(vbox),hbox,FALSE,FALSE,10);

	checkbutton=create_text_checkbutton("不使用时隐藏输入条",key_fcitx_apperance[0],g_strconcat(script_fcitx," banner_mode",NULL),NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("显示打字速度",key_fcitx_apperance[1],g_strconcat(script_fcitx," show_type_speed",NULL),NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("显示版本",key_fcitx_apperance[2],g_strconcat(script_fcitx," show_version",NULL),NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	return main_vbox; 
}
