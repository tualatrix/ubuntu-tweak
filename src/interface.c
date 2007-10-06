#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"
#include "about.h"
#include "startup.h"
#include "session_page.h"
#include "desktop.h"
#include "security.h"
#include "applications.h"
#include "system.h"

const gchar *startup_image=PACKAGE_PIXMAPS_DIR"/startup.png";
const gchar *desktop_image=PACKAGE_PIXMAPS_DIR"/desktop.png";
const gchar *system_image=PACKAGE_PIXMAPS_DIR"/system.png";
const gchar *security_image=PACKAGE_PIXMAPS_DIR"/security.png";
const gchar *applications_image=PACKAGE_PIXMAPS_DIR"/applications.png";
const gchar *banner_pic=PACKAGE_PIXMAPS_DIR"/ut_banner_pic.png";
const gchar *icon=PACKAGE_PIXMAPS_DIR"/ubuntu-tweak-icon.png";

GtkWidget *startup_notebook;
GtkWidget *desktop_notebook;
GtkWidget *security_notebook;
GtkWidget *applications_notebook;
GtkWidget *label_welcome;
GtkWidget *system_notebook;

gpointer *present;
GtkWidget *vbox_content_right;

void show_startup_notebook(GtkWidget *widget,gpointer data)
{
	if(GTK_WIDGET(present)!=startup_notebook){
		gtk_widget_hide(GTK_WIDGET(present));
		startup_notebook=create_startup_notebook();
		gtk_widget_show(startup_notebook);
		gtk_box_pack_start(GTK_BOX(vbox_content_right),startup_notebook,TRUE,TRUE,0);
		gtk_widget_show(startup_notebook);
		present=startup_notebook;
	}
}
void show_desktop_notebook(GtkWidget *widget,gpointer data)
{
	if(GTK_WIDGET(present)!=desktop_notebook){
		gtk_widget_hide(GTK_WIDGET(present));
		desktop_notebook=create_desktop_notebook();
		gtk_widget_show(desktop_notebook);
		gtk_box_pack_start(GTK_BOX(vbox_content_right),desktop_notebook,TRUE,TRUE,0);
		gtk_widget_show(desktop_notebook);
		present=desktop_notebook;
	}
}
void show_security_notebook(GtkWidget *widget,gpointer data)
{
	if(GTK_WIDGET(present)!=security_notebook){
		gtk_widget_hide(GTK_WIDGET(present));
		security_notebook=create_security_notebook();
		gtk_widget_show(security_notebook);
		gtk_box_pack_start(GTK_BOX(vbox_content_right),security_notebook,TRUE,TRUE,0);
		gtk_widget_show(security_notebook);
		present=security_notebook;
	}
}
void show_applications_notebook(GtkWidget *widget,gpointer data)
{
	if(GTK_WIDGET(present)!=applications_notebook){
		gtk_widget_hide(GTK_WIDGET(present));
		applications_notebook=create_applications_notebook();
		gtk_widget_show(applications_notebook);
		gtk_box_pack_start(GTK_BOX(vbox_content_right),applications_notebook,TRUE,TRUE,0);
		gtk_widget_show(applications_notebook);
		present=applications_notebook;
	}
}
void show_system_notebook(GtkWidget *widget,gpointer data)
{
	if(GTK_WIDGET(present)!=system_notebook){
		gtk_widget_hide(GTK_WIDGET(present));
		system_notebook=create_system_notebook();
		gtk_widget_show(system_notebook);
		gtk_box_pack_start(GTK_BOX(vbox_content_right),system_notebook,TRUE,TRUE,0);
		gtk_widget_show(system_notebook);
		present=system_notebook;
	}
}
GtkWidget *create_main_window(void)
{
/*定义主窗体和窗体上的一些盒子、按钮等*/
	GtkWidget *window;
	GtkWidget *headbanner;
	GtkWidget *vbox_main;
	GtkWidget *hbox_head;
	GtkWidget *hbox_content;
	GtkWidget *hbox_footer;
	GtkWidget *vbox_content_left;
	GtkWidget *separator;

/*定义底部的按钮盒按钮*/
	GtkWidget *vbutton;
	GtkWidget *hbutton;
	GtkWidget *button_ok;
	GtkWidget *button_exit;
	GtkWidget *button_about;

/*定义左侧工具栏的一些项目*/
	GtkWidget *toolbar;
	GtkWidget *startup_item;
	GtkWidget *startup_item_image;
	GtkWidget *desktop_item;
	GtkWidget *desktop_item_image;
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
	gtk_window_set_default_size(GTK_WINDOW(window),710,630);
	gtk_window_set_resizable(GTK_WINDOW(window),FALSE);
	gtk_container_set_border_width(GTK_CONTAINER(window),10);
	gtk_window_set_position(GTK_WINDOW(window),GTK_WIN_POS_CENTER);
	g_signal_connect(G_OBJECT(window),"delete_event",G_CALLBACK(gtk_main_quit),NULL);
	
/*创建界面最底层的竖盒，并将其加入到主窗体中，其他的盒子都将嵌入到这个盒子当中*/
	vbox_main=gtk_vbox_new(FALSE,0);
	gtk_widget_show(vbox_main);
	gtk_container_add(GTK_CONTAINER(window),vbox_main);

/*创建主窗体最上面的头部盒子，用于放置程序的LOGO等图片,定义为横盒是为了插入两张图片时，最大化不会影响布局*/
	hbox_head=gtk_hbox_new(FALSE,0);
	gtk_widget_show(hbox_head);
	gtk_box_pack_start(GTK_BOX(vbox_main),hbox_head,FALSE,FALSE,20);

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
	gtk_widget_set_size_request(separator,20,450);
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

/*insert LOGO to head area*/
	headbanner=gtk_image_new_from_file(banner_pic);
	gtk_widget_show(headbanner);
	gtk_box_pack_start(GTK_BOX(hbox_head),headbanner,FALSE,FALSE,0);

/*Welcome screen*/
	label_welcome=gtk_label_new(NULL);
	gtk_label_set_markup (GTK_LABEL (label_welcome),_("<span size=\"xx-large\">Welcome to <b>Ubuntu Tweak!</b></span>\n\n\nThis is a tool for Ubuntu which makes it easy to change hidden \n system and desktop settings.\n\nUbuntu Tweak is currently only for the GNOME Desktop Environment.\n\nAlthough this application is only in early stages, I will keep developing it.\n\nIf you have any suggestions, please e-mail me. \n\nThankyou,\nTualatriX"));
	gtk_label_set_justify(GTK_LABEL(label_welcome),GTK_JUSTIFY_FILL);
	gtk_widget_show(label_welcome);
	gtk_container_set_border_width(GTK_CONTAINER(vbox_content_right),10);
	gtk_box_pack_start(GTK_BOX(vbox_content_right),label_welcome,FALSE,FALSE,0);

	present=label_welcome;

/*创建左侧工具条*/
	toolbar=gtk_toolbar_new();
	gtk_widget_show(toolbar);
	gtk_toolbar_set_orientation(GTK_TOOLBAR(toolbar),GTK_ORIENTATION_VERTICAL);
	gtk_toolbar_set_style(GTK_TOOLBAR(toolbar),GTK_TOOLBAR_BOTH_HORIZ);

	startup_item_image=gtk_image_new_from_file(startup_image);
	desktop_item_image=gtk_image_new_from_file(desktop_image);
	system_item_image=gtk_image_new_from_file(system_image);
	security_item_image=gtk_image_new_from_file(security_image);
	applications_item_image=gtk_image_new_from_file(applications_image);

	startup_item=gtk_toolbar_append_item(GTK_TOOLBAR(toolbar),
			_("Startup"),
			_("Session settings, change the Splash Screen, or change Services (to be implemented)"),
			"Private",
			startup_item_image,
			GTK_SIGNAL_FUNC(show_startup_notebook),
			NULL);

	desktop_item=gtk_toolbar_append_item(GTK_TOOLBAR(toolbar),
			_("Desktop"),
			_("Change the Desktop Icons, and other options relating to the Desktop"),
			"Private",
			desktop_item_image,
			GTK_SIGNAL_FUNC(show_desktop_notebook),
			NULL);

	system_item=gtk_toolbar_append_item(GTK_TOOLBAR(toolbar),
			_("System"),
			_("Configuration of Power Management, and other hardware settings"),
			"Private",
			system_item_image,
			GTK_SIGNAL_FUNC(show_system_notebook),
			NULL);

	security_item=gtk_toolbar_append_item(GTK_TOOLBAR(toolbar),
			_("Security"),
			_("Options relating to security of the system"),
			"Private",
			security_item_image,
			GTK_SIGNAL_FUNC(show_security_notebook),
			NULL);

	applications_item=gtk_toolbar_append_item(GTK_TOOLBAR(toolbar),
			_("Applications"),
			_("Configuration options for commonly-used applications"),
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

	button_ok=gtk_button_new_from_stock(GTK_STOCK_OK);
	g_signal_connect(GTK_OBJECT(button_ok),"clicked",G_CALLBACK(button_test),NULL);
	gtk_widget_show(button_ok);
	gtk_container_add(GTK_CONTAINER(hbutton),button_ok);

	button_exit=gtk_button_new_from_stock(GTK_STOCK_QUIT);
	g_signal_connect(GTK_OBJECT(button_exit),"clicked",G_CALLBACK(gtk_main_quit),NULL);
	gtk_widget_show(button_exit);
	gtk_container_add(GTK_CONTAINER(hbutton),button_exit);

	button_about=gtk_button_new_from_stock(GTK_STOCK_ABOUT);
	g_signal_connect(GTK_OBJECT(button_about),"clicked",G_CALLBACK(show_about),NULL);
	gtk_widget_show(button_about);
	gtk_container_add(GTK_CONTAINER(vbutton),button_about);

	return window;
}
