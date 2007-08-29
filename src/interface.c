#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"
#include "about.h"
#include "startup.h"
#include "session_page.h"
#include "personality.h"
#include "security.h"
#include "applications.h"

gchar *startup_image=PACKAGE_PIXMAPS_DIR"/startup.png";
gchar *personality_image=PACKAGE_PIXMAPS_DIR"/desktop.png";
gchar *other_image=PACKAGE_PIXMAPS_DIR"/apperance.png";
gchar *security_image=PACKAGE_PIXMAPS_DIR"/security.png";
gchar *applications_image=PACKAGE_PIXMAPS_DIR"/applications.png";
gchar *header_left=PACKAGE_PIXMAPS_DIR"/ut_header_left.png";
gchar *header_right=PACKAGE_PIXMAPS_DIR"/ut_header_right.png";
gchar *icon=PACKAGE_PIXMAPS_DIR"/ubuntu-tweak-icon.png";

GtkWidget *startup_notebook;
GtkWidget *personality_notebook;
GtkWidget *security_notebook;
GtkWidget *applications_notebook;
GtkWidget *label_welcome;

void show_startup_notebook(GtkWidget *widget,gpointer data)
{
	gtk_widget_hide(label_welcome);
	gtk_widget_hide(personality_notebook);
	gtk_widget_hide(security_notebook);
	gtk_widget_hide(applications_notebook);
	gtk_widget_show(startup_notebook);
}
void show_personality_notebook(GtkWidget *widget,gpointer data)
{
	gtk_widget_hide(label_welcome);
	gtk_widget_hide(startup_notebook);
	gtk_widget_hide(security_notebook);
	gtk_widget_hide(applications_notebook);
	gtk_widget_show(personality_notebook);
}
void show_security_notebook(GtkWidget *widget,gpointer data)
{
	gtk_widget_hide(label_welcome);
	gtk_widget_hide(startup_notebook);
	gtk_widget_hide(personality_notebook);
	gtk_widget_hide(applications_notebook);
	gtk_widget_show(security_notebook);
}
void show_applications_notebook(GtkWidget *widget,gpointer data)
{
	gtk_widget_hide(label_welcome);
	gtk_widget_hide(startup_notebook);
	gtk_widget_hide(personality_notebook);
	gtk_widget_hide(security_notebook);
	gtk_widget_show(applications_notebook);
}
GtkWidget *create_main_window(void)
{
/*定义主窗体和窗体上的一些盒子、按钮等*/
	GtkWidget *window;
	GtkWidget *headline;
	GtkWidget *headline_2;
	GtkWidget *vbox_main;
	GtkWidget *hbox_head;
	GtkWidget *hbox_content;
	GtkWidget *hbox_footer;
	GtkWidget *vbox_content_left;
	GtkWidget *vbox_content_right;
	GtkWidget *hbox;
	GtkWidget *label_temp;
	GtkWidget *label_now;
	GtkWidget *label_want;
	GtkWidget *sitting_now;
	GtkWidget *input;

	GtkWidget *separator;
	gchar *str=NULL;

/*定义底部的按钮盒按钮*/
	GtkWidget *vbutton;
	GtkWidget *hbutton;
	GtkWidget *button_ok;
	GtkWidget *button_exit;
	GtkWidget *button_about;

	
/*定义左侧工具栏的一些项目*/
	GtkWidget *toolbar;
	GtkWidget *gnome_item;
	GtkWidget *gnome_item_image;
	GtkWidget *ubuntu_item;
	GtkWidget *ubuntu_item_image;
	GtkWidget *system_item;
	GtkWidget *system_item_image;
	GtkWidget *security_item;
	GtkWidget *security_item_image;
	GtkWidget *applications_item;
	GtkWidget *applications_item_image;


/*设定程序的图标，主要用于任务栏、dock上的显示*/

	gtk_window_set_default_icon_from_file(icon,NULL);

/*创建程序主窗体，分别设定好窗口标题，窗口默认大小，窗口默认打开位置（屏幕中心）*/
	window=gtk_window_new(GTK_WINDOW_TOPLEVEL);
	gtk_window_set_title(GTK_WINDOW(window),"Ubuntu Tweak");
	gtk_container_set_border_width(GTK_CONTAINER(window),10);
//	gtk_window_set_default_size(GTK_WINDOW(window),660,490);
	gtk_window_set_position(GTK_WINDOW(window),GTK_WIN_POS_CENTER);
	g_signal_connect(G_OBJECT(window),"delete_event",G_CALLBACK(gtk_main_quit),NULL);
	
/*创建界面最底层的竖盒，并将其加入到主窗体中，其他的盒子都将嵌入到这个盒子当中*/
	vbox_main=gtk_vbox_new(FALSE,0);
	gtk_widget_show(vbox_main);
	gtk_container_add(GTK_CONTAINER(window),vbox_main);

/*创建主窗体最上面的头部盒子，用于放置程序的LOGO等图片,定义为横盒是为了插入两张图片时，最大化不会影响布局*/
	hbox_head=gtk_hbox_new(FALSE,0);
	gtk_widget_show(hbox_head);
	gtk_box_pack_start(GTK_BOX(vbox_main),hbox_head,FALSE,FALSE,0);

/*创建主窗体内容盒子，为横盒，因为内容还将有左侧工具条和右侧主内容*/
	hbox_content=gtk_hbox_new(FALSE,0);
	gtk_widget_show(hbox_content);
	gtk_box_pack_start(GTK_BOX(vbox_main),hbox_content,FALSE,FALSE,0);

/*创建主窗体内容左侧盒子*/
	vbox_content_left=gtk_vbox_new(FALSE,0);
	gtk_widget_show(vbox_content_left);
	gtk_box_pack_start(GTK_BOX(hbox_content),vbox_content_left,FALSE,FALSE,0);

/*创建工具条与内容区域的一条分隔线*/
	separator=gtk_vseparator_new();
	gtk_widget_set_size_request(separator,10,400);
	gtk_box_pack_start(GTK_BOX(hbox_content),separator,FALSE,FALSE,0);
	gtk_widget_show(separator);

/*右侧内容竖盒*/
	vbox_content_right=gtk_vbox_new(FALSE,0);
	gtk_widget_show(vbox_content_right);
	gtk_box_pack_start(GTK_BOX(hbox_content),vbox_content_right,TRUE,TRUE,0);

/*程序主界面最下面的内容，用于放几个按钮*/
	hbox_footer=gtk_hbox_new(FALSE,0);
	gtk_widget_show(hbox_footer);
	gtk_box_pack_end(GTK_BOX(vbox_main),hbox_footer,FALSE,FALSE,0);

/*将LOGO插入head区域*/
	headline=gtk_image_new_from_file(header_left);
	gtk_widget_show(headline);
	gtk_box_pack_start(GTK_BOX(hbox_head),headline,FALSE,FALSE,0);

	headline_2=gtk_image_new_from_file(header_right);
	gtk_widget_show(headline_2);
	gtk_box_pack_end(GTK_BOX(hbox_head),headline_2,FALSE,FALSE,0);

/*正文默认的欢迎字样*/

	label_welcome=gtk_label_new(g_get_user_data_dir());
	gtk_label_set_justify(GTK_LABEL(label_welcome),GTK_JUSTIFY_LEFT);
	gtk_widget_show(label_welcome);
	gtk_container_set_border_width(GTK_CONTAINER(vbox_content_right),10);
	gtk_box_pack_start(GTK_BOX(vbox_content_right),label_welcome,FALSE,FALSE,0);


	startup_notebook=create_startup_notebook();
	gtk_box_pack_start(GTK_BOX(vbox_content_right),startup_notebook,TRUE,TRUE,0);
	

	personality_notebook=create_personality_notebook();

	gtk_box_pack_start(GTK_BOX(vbox_content_right),personality_notebook,TRUE,TRUE,0);

	security_notebook=create_security_notebook();

	gtk_box_pack_start(GTK_BOX(vbox_content_right),security_notebook,TRUE,TRUE,0);

	applications_notebook=create_applications_notebook();

	gtk_box_pack_start(GTK_BOX(vbox_content_right),applications_notebook,TRUE,TRUE,0);

/*创建左侧工具条*/
	toolbar=gtk_toolbar_new();
	gtk_widget_show(toolbar);
	gtk_toolbar_set_orientation(GTK_TOOLBAR(toolbar),GTK_ORIENTATION_VERTICAL);
	gtk_toolbar_set_style(GTK_TOOLBAR(toolbar),GTK_TOOLBAR_BOTH_HORIZ);

	gnome_item_image=gtk_image_new_from_file(startup_image);
	ubuntu_item_image=gtk_image_new_from_file(personality_image);
	system_item_image=gtk_image_new_from_file(other_image);
	security_item_image=gtk_image_new_from_file(security_image);
	applications_item_image=gtk_image_new_from_file(applications_image);

	gnome_item=gtk_toolbar_append_item(GTK_TOOLBAR(toolbar),
			_("Startup"),
			"有关系统启动的选项",
			"Private",
			gnome_item_image,
			GTK_SIGNAL_FUNC(show_startup_notebook),
			NULL);

	ubuntu_item=gtk_toolbar_append_item(GTK_TOOLBAR(toolbar),
			_("Personalization"),
			"哈哈哈哈",
			"Private",
			ubuntu_item_image,
			GTK_SIGNAL_FUNC(show_personality_notebook),
			NULL);

	system_item=gtk_toolbar_append_item(GTK_TOOLBAR(toolbar),
			_("Appearance"),
			"wow~~~",
			"Private",
			system_item_image,
			GTK_SIGNAL_FUNC(NULL),
			NULL);

	security_item=gtk_toolbar_append_item(GTK_TOOLBAR(toolbar),
			_("Security"),
			"安全第一啊！",
			"Private",
			security_item_image,
			GTK_SIGNAL_FUNC(show_security_notebook),
			NULL);

	applications_item=gtk_toolbar_append_item(GTK_TOOLBAR(toolbar),
			_("Softwares"),
			"设置应用软件吧！",
			"Private",
			applications_item_image,
			GTK_SIGNAL_FUNC(show_applications_notebook),
			NULL);

	gtk_box_pack_start(GTK_BOX(vbox_content_left),toolbar,FALSE,FALSE,0);

/*主窗体最底部的几个按钮*/

	vbutton=gtk_vbutton_box_new();
	gtk_widget_show(vbutton);
	gtk_box_pack_start(GTK_BOX(hbox_footer),vbutton,FALSE,FALSE,0);

	hbutton=gtk_hbutton_box_new();
	gtk_box_set_spacing(GTK_BOX(hbutton),10);
	gtk_widget_show(hbutton);
	gtk_box_pack_end(GTK_BOX(hbox_footer),hbutton,FALSE,FALSE,0);

	button_ok=gtk_button_new_with_mnemonic(_("OK"));
	gtk_widget_show(button_ok);
	gtk_container_add(GTK_CONTAINER(hbutton),button_ok);

	button_exit=gtk_button_new_with_mnemonic(_("Exit"));
	g_signal_connect(GTK_OBJECT(button_exit),"clicked",G_CALLBACK(gtk_main_quit),NULL);
	gtk_widget_show(button_exit);
	gtk_container_add(GTK_CONTAINER(hbutton),button_exit);

	button_about=gtk_button_new_with_mnemonic(_("About"));
	g_signal_connect(GTK_OBJECT(button_about),"clicked",G_CALLBACK(show_about),NULL);
	gtk_widget_show(button_about);
	gtk_container_add(GTK_CONTAINER(vbutton),button_about);

	return window;
}
