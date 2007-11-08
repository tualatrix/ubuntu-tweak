#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"
#include "session_page.h"
#include "icon_page.h"
#include "compiz_page.h"
#include "gnome_page.h"
#include "nautilus_page.h"
#include "powermanager_page.h"
#include "security_page.h"
#include "about.h"

#define	UT_LOGO		PACKAGE_PIXMAPS_DIR"/ubuntu-tweak.png"
#define UT_BANNER	PACKAGE_PIXMAPS_DIR"/banner.png"
#define UT_WELCOME	PACKAGE_PIXMAPS_DIR"/welcome.png"
#define UT_STARTUP	PACKAGE_PIXMAPS_DIR"/startup.png"
#define UT_DESKTOP	PACKAGE_PIXMAPS_DIR"/desktop.png"
#define UT_ICON		PACKAGE_PIXMAPS_DIR"/icon.png"
#define UT_COMPIZ	PACKAGE_PIXMAPS_DIR"/compiz-fusion.png"
#define UT_GNOME	PACKAGE_PIXMAPS_DIR"/gnome.png"
#define UT_NAUTILUS	PACKAGE_PIXMAPS_DIR"/nautilus.png"
#define UT_SYSTEM	PACKAGE_PIXMAPS_DIR"/system.png"
#define UT_POWER	PACKAGE_PIXMAPS_DIR"/power-manager.png"
#define UT_SECURITY	PACKAGE_PIXMAPS_DIR"/security.png"
#define UT_SECU_OPTIONS	PACKAGE_PIXMAPS_DIR"/security-options.png"
#define UT_APPLICATION	PACKAGE_PIXMAPS_DIR"/applications.png"
#define UT_SESSION	PACKAGE_PIXMAPS_DIR"/session-properties.png"

enum
{
	COL_NUM = 0,
	COL_ICON,
	COL_TEXT,
	NUM_COLS
};

enum
{
	ITEM_FATHER,
	ITEM_CHILD
};

enum
{
	PAGE_WELCOME = 0,
	PAGE_SATRUP,
		PAGE_SESSION,
	PAGE_DESKTOP,
		PAGE_ICON,
		PAGE_COMPIZ,
		PAGE_GNOME,
		PAGE_NAUTILUS,
	PAGE_SYSTEM,
		PAGE_POWER,
	PAGE_SECUTIRY,
		PAGE_SECU_OPTTIONS,
	PAGE_APPLICATION,
	NUM_PAGE
};

typedef struct
{
	gint tree_type;
	gint page_num;
	gchar *icon;
	gchar *name;
}TweakItem;

TweakItem list[]=
{
	{ITEM_FATHER,PAGE_WELCOME,UT_WELCOME,"欢迎使用"},
	{ITEM_FATHER,PAGE_SATRUP,UT_STARTUP,"启动控制"},
		{ITEM_CHILD,PAGE_SESSION,UT_SESSION,"会话控制"},
	{ITEM_FATHER,PAGE_DESKTOP,UT_DESKTOP,"桌面设置"},
		{ITEM_CHILD,PAGE_ICON,UT_ICON,"桌面图标"},
		{ITEM_CHILD,PAGE_COMPIZ,UT_COMPIZ,"Compiz"},
		{ITEM_CHILD,PAGE_GNOME,UT_GNOME,"GNOME设置"},
		{ITEM_CHILD,PAGE_NAUTILUS,UT_NAUTILUS,"文件管理器"},
	{ITEM_FATHER,PAGE_SYSTEM,UT_SYSTEM,"系统设置"},
		{ITEM_CHILD,PAGE_POWER,UT_POWER,"高级电源管理"},
	{ITEM_FATHER,PAGE_SECUTIRY,UT_SECURITY,"安全相关"},
		{ITEM_CHILD,PAGE_SECU_OPTTIONS,UT_SECU_OPTIONS,"安全设置"},
	{ITEM_FATHER,PAGE_APPLICATION,UT_APPLICATION,"应用程序"},
	{ITEM_FATHER,NUM_PAGE,NULL,NULL}
};

static	GtkWidget *notebook;

GtkWidget *create_notebook(void)
{
	GtkWidget *notebook;
	GtkWidget *vbox,*hbox;
	GtkWidget *label,*page_label;
	
	notebook=gtk_notebook_new();
	gtk_notebook_set_tab_pos(GTK_NOTEBOOK(notebook),GTK_POS_TOP);
	gtk_notebook_set_show_tabs(GTK_NOTEBOOK(notebook),FALSE);

	/*no.1 page-welcome*/
	label=gtk_label_new(NULL);
	gtk_label_set_markup (GTK_LABEL (label),_("<span size=\"xx-large\">Welcome to <b>Ubuntu Tweak!</b></span>\n\n\nThis is a tool for Ubuntu which makes it easy to change hidden \n system and desktop settings.\n\nUbuntu Tweak is currently only for the GNOME Desktop Environment.\n\nAlthough this application is only in early stages, I will keep developing it.\n\nIf you have any suggestions, please e-mail me. \n\nThankyou,\n- TualatriX"));
	gtk_label_set_justify(GTK_LABEL(label),GTK_JUSTIFY_FILL);
	page_label=gtk_label_new("欢迎使用");
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),label,page_label);

//	label=gtk_label_new("欢迎进入启动控制");
	hbox=gtk_hbox_new(FALSE,0);
	label=gtk_tool_button_new_from_stock(GTK_STOCK_OK);
	gtk_box_pack_start(GTK_BOX(hbox),label,FALSE,FALSE,0);
	gtk_tool_button_set_label(GTK_TOOL_BUTTON(label),"hello");
	label=gtk_tool_button_new_from_stock(GTK_STOCK_ABOUT);
	gtk_box_pack_start(GTK_BOX(hbox),label,FALSE,FALSE,0);
	page_label=gtk_label_new("启动控制");
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),hbox,page_label);
	
	vbox=create_session_page();
	page_label=gtk_label_new("会话设置");
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),vbox,page_label);

	label=gtk_label_new("欢迎进入桌面设置");
	page_label=gtk_label_new("桌面设置");
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),label,page_label);

	vbox=create_icon_page();
	page_label=gtk_label_new("桌面图标");
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),vbox,page_label);

	vbox=create_compiz_page();
	page_label=gtk_label_new("Compiz设置");
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),vbox,page_label);

	vbox=create_gnome_page();
	page_label=gtk_label_new("GNOME");
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),vbox,page_label);

	vbox=create_nautilus_page();
	page_label=gtk_label_new("nautilus");
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),vbox,page_label);

	label=gtk_label_new("系统设置");
	page_label=gtk_label_new("欢迎进入系统设置");
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),label,page_label);

	vbox=create_powermanager_page();
	page_label=gtk_label_new("powermanager");
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),vbox,page_label);

	label=gtk_label_new("安全设置");
	page_label=gtk_label_new("欢迎进入安全设置");
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),label,page_label);

	vbox=create_disable_page();
	page_label=gtk_label_new("security");
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),vbox,page_label);

	return notebook;
}

static void
selection_cb(GtkTreeSelection *selection,
		GtkTreeModel *model)
{
	GtkTreeIter iter;
	GValue value={0,};
	
	if(!gtk_tree_selection_get_selected(selection,NULL,&iter))
		return;

	gtk_tree_model_get_value(model,&iter,
			COL_NUM,&value);

	gtk_notebook_set_current_page(GTK_NOTEBOOK(notebook),g_value_get_int(&value));

	g_value_unset(&value);
}

GtkTreeStore *
create_liststore(void)
{
	GtkTreeStore *store;
	GtkTreeIter 	child,iter;
	GdkPixbuf     *icon;
	GError        *error = NULL;
	gint		i=0,j;

	store = gtk_tree_store_new(NUM_COLS, G_TYPE_INT, GDK_TYPE_PIXBUF, G_TYPE_STRING);

	while(list[i].name != NULL)
	{
		if(list[i].tree_type == ITEM_FATHER)
		{
			icon = gdk_pixbuf_new_from_file(list[i].icon, &error);

			j=i+1;

			gtk_tree_store_append(store,&iter,NULL);
			gtk_tree_store_set(store,&iter,
					COL_NUM,list[i].page_num,
					COL_ICON,icon,
					COL_TEXT,list[i].name,
					-1);
		}
		else
		{
			icon = gdk_pixbuf_new_from_file(list[i].icon, &error);

			gtk_tree_store_append(store,&child,&iter);
			gtk_tree_store_set(store,&child,
					COL_NUM,list[i].page_num,
					COL_ICON,icon,
					COL_TEXT,list[i].name,
					-1);
		}
		
		i++;
	}	
					
	return store;
}

GtkWidget *
create_treeview(void)
{
	GtkTreeModel		*model;
	GtkTreeIter		iter;
	GtkTreeViewColumn	*col;
	GtkTreeSelection	*selection;
	GtkCellRenderer		*renderer;
	GtkWidget		*tree_view;

	model = GTK_TREE_MODEL(create_liststore());
	tree_view = gtk_tree_view_new_with_model(model);
	selection=gtk_tree_view_get_selection(GTK_TREE_VIEW(tree_view));
	gtk_tree_selection_set_mode(GTK_TREE_SELECTION(selection),
					GTK_SELECTION_BROWSE);

	renderer = gtk_cell_renderer_text_new();
	col=gtk_tree_view_column_new_with_attributes("num",renderer,
							"text",COL_NUM,NULL);
	gtk_tree_view_column_set_visible(col,FALSE);
	gtk_tree_view_append_column(GTK_TREE_VIEW(tree_view), col);

	col = gtk_tree_view_column_new();
	gtk_tree_view_column_set_title(col, "Title");

	renderer = gtk_cell_renderer_pixbuf_new();
	gtk_tree_view_column_pack_start(col, renderer, FALSE);
	gtk_tree_view_column_set_attributes(col, renderer,
					    "pixbuf", COL_ICON,
					    NULL);
	renderer = gtk_cell_renderer_text_new();
	gtk_tree_view_column_pack_start(col, renderer, TRUE);
	gtk_tree_view_column_set_attributes(col, renderer,
					    "text", COL_TEXT,
					    NULL);

	gtk_tree_view_set_headers_visible(GTK_TREE_VIEW(tree_view),FALSE);
	gtk_tree_view_append_column(GTK_TREE_VIEW(tree_view), col);

	gtk_tree_model_get_iter_first(GTK_TREE_MODEL(model),&iter);
	gtk_tree_selection_select_iter(GTK_TREE_SELECTION(selection),&iter);
	
	g_signal_connect(selection,"changed",G_CALLBACK(selection_cb),model);

	gtk_widget_show_all(tree_view);

	return tree_view;
}

GtkWidget *create_main_window(void)
{
	GtkWidget *window;
	GtkWidget *tree_view;
	GtkWidget *scrolled_window;
	GtkWidget *banner;
	GtkWidget *vbox,*hbox;
	GtkWidget *button;

	gtk_window_set_default_icon_from_file(UT_LOGO,NULL);
/*创建主窗体，分别设置好窗口标题，默认尺寸，是否可调，默认放置位置，边框
 *并连接关闭的信号
 */ 
	window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
	gtk_window_set_title(GTK_WINDOW(window),"Ubuntu Tweak!");
	gtk_widget_set_size_request(GTK_WIDGET(window),650,680);
	gtk_window_set_resizable(GTK_WINDOW(window),FALSE);
	gtk_container_set_border_width(GTK_CONTAINER(window),10);
	gtk_window_set_position(GTK_WINDOW(window),GTK_WIN_POS_CENTER);
	g_signal_connect(window, "delete_event", gtk_main_quit, NULL); 

/*创建窗体的主vbox*/
	vbox=gtk_vbox_new(FALSE,0);
	gtk_container_add(GTK_CONTAINER(window),vbox);

/*将banner插入主vbox中*/
	banner=gtk_image_new_from_file(UT_BANNER);
	gtk_box_pack_start(GTK_BOX(vbox),banner,FALSE,FALSE,0);

/*创建一个hbox，用于包装Tree View和Notebook*/
	hbox=gtk_hbox_new(FALSE,5);
	gtk_box_pack_start(GTK_BOX(vbox),hbox,TRUE,TRUE,0);

/*创建Tree View，将其包装进scrolled_window里，再装进hbox里*/
	tree_view = create_treeview();
	scrolled_window=gtk_scrolled_window_new(NULL,NULL);
	gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(scrolled_window),
					GTK_POLICY_NEVER,
					GTK_POLICY_AUTOMATIC);
	gtk_box_pack_start(GTK_BOX(hbox),scrolled_window,FALSE,FALSE,0);
	gtk_container_add(GTK_CONTAINER(scrolled_window),tree_view);

/*创建notebook，包装进hbox里*/
	notebook=create_notebook();
	gtk_box_pack_start(GTK_BOX(hbox),notebook,TRUE,TRUE,0);

/*窗体下部的hbox，用于放置几个按钮*/
	hbox=gtk_hbox_new(FALSE,5);
	gtk_box_pack_start(GTK_BOX(vbox),hbox,FALSE,FALSE,5);

	button=gtk_button_new_from_stock(GTK_STOCK_ABOUT);
	g_signal_connect((button),"clicked",G_CALLBACK(show_about),NULL);
	gtk_box_pack_start(GTK_BOX(hbox),button,FALSE,FALSE,0);

	button=gtk_button_new_from_stock(GTK_STOCK_QUIT);
	g_signal_connect(button,"clicked",G_CALLBACK(gtk_main_quit),NULL);
	gtk_box_pack_end(GTK_BOX(hbox),button,FALSE,FALSE,0);
	
	button=gtk_button_new_from_stock(GTK_STOCK_OK);
	gtk_box_pack_end(GTK_BOX(hbox),button,FALSE,FALSE,0);

	return window;
}
