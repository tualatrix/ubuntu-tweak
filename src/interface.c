#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "interface.h"

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
		PAGE_FCITX,
	NUM_PAGE
};

typedef struct
{
	gint tree_type;
	gint page_num;
	gchar *icon;
}TweakItem;

TweakItem list[]=
{
	{ITEM_FATHER,PAGE_WELCOME,UT_WELCOME},
	{ITEM_FATHER,PAGE_SATRUP,UT_STARTUP},
		{ITEM_CHILD,PAGE_SESSION,UT_SESSION},
	{ITEM_FATHER,PAGE_DESKTOP,UT_DESKTOP},
		{ITEM_CHILD,PAGE_ICON,UT_ICON},
		{ITEM_CHILD,PAGE_COMPIZ,UT_COMPIZ},
		{ITEM_CHILD,PAGE_GNOME,UT_GNOME},
		{ITEM_CHILD,PAGE_NAUTILUS,UT_NAUTILUS},
	{ITEM_FATHER,PAGE_SYSTEM,UT_SYSTEM},
		{ITEM_CHILD,PAGE_POWER,UT_POWER},
	{ITEM_FATHER,PAGE_SECUTIRY,UT_SECURITY},
		{ITEM_CHILD,PAGE_SECU_OPTTIONS,UT_SECU_OPTIONS},
	{ITEM_FATHER,PAGE_APPLICATION,UT_APPLICATION},
		{ITEM_CHILD,PAGE_FCITX,UT_SECU_OPTIONS},
	{ITEM_FATHER,NUM_PAGE,NULL}
};

static	GtkWidget *notebook;

GtkWidget *create_notebook(void)
{
	GtkWidget *notebook;
	GtkWidget *vbox;
	GtkWidget *label,*page_label;
	
	notebook=gtk_notebook_new();
	gtk_notebook_set_tab_pos(GTK_NOTEBOOK(notebook),GTK_POS_TOP);
	gtk_notebook_set_scrollable (GTK_NOTEBOOK(notebook),TRUE);
	gtk_notebook_set_show_tabs(GTK_NOTEBOOK(notebook),FALSE);

	/*no.1 page-welcome*/
	vbox=gtk_vbox_new(FALSE,0);

	label=gtk_label_new(NULL);
	gtk_label_set_markup (GTK_LABEL (label),_("<span size=\"xx-large\">Welcome to <b>Ubuntu Tweak!</b></span>\n\n\nThis is a tool for Ubuntu which makes it easy to change hidden \nsystem and desktop settings.\n\nUbuntu Tweak is currently only for the GNOME Desktop Environment.\n\nAlthough this application is only in early stages, I'll keep developing it.\n\nIf you have any suggestions, Please E-mail me. \n\nThank You!"));
	gtk_label_set_justify(GTK_LABEL(label),GTK_JUSTIFY_FILL);
	gtk_box_pack_start(GTK_BOX(vbox),label,FALSE,FALSE,20);

	page_label=gtk_label_new(_("Welcome"));
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),vbox,page_label);

	label=gtk_label_new(NULL);
	gtk_label_set_markup(GTK_LABEL(label),_("<span size=\"large\">Welcome to Startup Page.</span>\n\n\nHere, You can set Session Settings, change the Splash Screen, \nor change Services (to be implemented)"));
	page_label=gtk_label_new("Startup");
	gtk_label_set_justify(GTK_LABEL(label),GTK_JUSTIFY_CENTER);
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),label,page_label);
	
	vbox=create_session_page();
	page_label=gtk_label_new("Session Control");
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),vbox,page_label);

	label=gtk_label_new(NULL);
	gtk_label_set_markup(GTK_LABEL(label),_("<span size=\"large\">Welcome to Desktop Page.</span>\n\n\nHere, You can change the desktop icons, and other options\n relating to the Desktop"));
	gtk_label_set_justify(GTK_LABEL(label),GTK_JUSTIFY_CENTER);
	page_label=gtk_label_new("Desktop");
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),label,page_label);

	vbox=create_icon_page();
	page_label=gtk_label_new("Desktop Icon");
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),vbox,page_label);

	vbox=create_compiz_page();
	page_label=gtk_label_new("Compiz Fusion");
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),vbox,page_label);

	vbox=create_gnome_page();
	page_label=gtk_label_new("GNOME");
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),vbox,page_label);

	vbox=create_nautilus_page();
	page_label=gtk_label_new("Nautilus");
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),vbox,page_label);

	label=gtk_label_new(NULL);
	gtk_label_set_markup(GTK_LABEL(label),_("<span size=\"large\">Welcome to System Page.</span>\n\n\nHere, You can configuration of Power Management, and\n other hardware settings"));
	gtk_label_set_justify(GTK_LABEL(label),GTK_JUSTIFY_CENTER);
	page_label=gtk_label_new("System");
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),label,page_label);

	vbox=create_powermanager_page();
	page_label=gtk_label_new("Powermanager");
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),vbox,page_label);

	label=gtk_label_new(NULL);
	gtk_label_set_markup(GTK_LABEL(label),_("<span size=\"large\">Welcome to Security Page.</span>\n\n\nHere are some options relating to security of the system"));
	gtk_label_set_justify(GTK_LABEL(label),GTK_JUSTIFY_CENTER);
	page_label=gtk_label_new("Security");
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),label,page_label);

	vbox=create_disable_page();
	page_label=gtk_label_new("Disable");
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),vbox,page_label);

	label=gtk_label_new(NULL);
	gtk_label_set_markup(GTK_LABEL(label),_("<span size=\"large\">Welcome to Applications Page.</span>\n\n\nConfiguration options for commonly-used applications"));
	gtk_label_set_justify(GTK_LABEL(label),GTK_JUSTIFY_CENTER);
	page_label=gtk_label_new("Applications");
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),label,page_label);

	vbox=create_fcitx_page();
	page_label=gtk_label_new("Fcitx");
	gtk_notebook_append_page(GTK_NOTEBOOK(notebook),vbox,page_label);

	return notebook;
}

GtkTreeStore *
create_liststore(void)
{
	GtkTreeStore	*store;
	GtkTreeIter 	child,iter;
	GdkPixbuf	*icon;
	GError		*error = NULL;
	gint		i=0,j;

	store = gtk_tree_store_new(NUM_COLS, G_TYPE_INT, GDK_TYPE_PIXBUF, G_TYPE_STRING);

	while(list[i].icon != NULL)
	{
		/*通过判断是否有ITEM_FATHER值来创建相应的父树，否则创建子树*/
		if(list[i].tree_type == ITEM_FATHER)
		{
			icon = gdk_pixbuf_new_from_file(list[i].icon, &error);

			j=i+1;

			gtk_tree_store_append(store,&iter,NULL);

			if(i==PAGE_WELCOME){
				gtk_tree_store_set(store,&iter,
						COL_NUM,list[i].page_num,
						COL_ICON,icon,
						COL_TEXT,_("Welcome"),
						-1);
			}
			else if(i==PAGE_SATRUP){
				gtk_tree_store_set(store,&iter,
						COL_NUM,list[i].page_num,
						COL_ICON,icon,
						COL_TEXT,_("Startup"),
						-1);
			}
			else if(i==PAGE_DESKTOP){
				gtk_tree_store_set(store,&iter,
						COL_NUM,list[i].page_num,
						COL_ICON,icon,
						COL_TEXT,_("Desktop"),
						-1);
			}
			else if(i==PAGE_SYSTEM){
				gtk_tree_store_set(store,&iter,
						COL_NUM,list[i].page_num,
						COL_ICON,icon,
						COL_TEXT,_("System"),
						-1);
			}
			else if(i==PAGE_SECUTIRY){
				gtk_tree_store_set(store,&iter,
						COL_NUM,list[i].page_num,
						COL_ICON,icon,
						COL_TEXT,_("Security"),
						-1);
			}
			else if(i==PAGE_APPLICATION){
				gtk_tree_store_set(store,&iter,
						COL_NUM,list[i].page_num,
						COL_ICON,icon,
						COL_TEXT,_("Applications"),
						-1);
			}
			
		}
		else
		{
			icon = gdk_pixbuf_new_from_file(list[i].icon, &error);

			gtk_tree_store_append(store,&child,&iter);

			if(i==PAGE_SESSION){
				gtk_tree_store_set(store,&child,
						COL_NUM,list[i].page_num,
						COL_ICON,icon,
						COL_TEXT,_("Session Control"),
						-1);
			}
			else if(i==PAGE_ICON){
				gtk_tree_store_set(store,&child,
						COL_NUM,list[i].page_num,
						COL_ICON,icon,
						COL_TEXT,_("Desktop Icon"),
						-1);
			}
			else if(i==PAGE_COMPIZ){
				gtk_tree_store_set(store,&child,
						COL_NUM,list[i].page_num,
						COL_ICON,icon,
						COL_TEXT,"Compiz Fusion",
						-1);
			}
			else if(i==PAGE_GNOME){
				gtk_tree_store_set(store,&child,
						COL_NUM,list[i].page_num,
						COL_ICON,icon,
						COL_TEXT,_("GNOME"),
						-1);
			}
			else if(i==PAGE_NAUTILUS){
				gtk_tree_store_set(store,&child,
						COL_NUM,list[i].page_num,
						COL_ICON,icon,
						COL_TEXT,_("Nautilus"),
						-1);
			}
			else if(i==PAGE_POWER){
				gtk_tree_store_set(store,&child,
						COL_NUM,list[i].page_num,
						COL_ICON,icon,
						COL_TEXT,_("Power Manager"),
						-1);
			}
			else if(i==PAGE_SECU_OPTTIONS){
				gtk_tree_store_set(store,&child,
						COL_NUM,list[i].page_num,
						COL_ICON,icon,
						COL_TEXT,_("Security Options"),
						-1);
			}
			else if(i==PAGE_FCITX){
				gtk_tree_store_set(store,&child,
						COL_NUM,list[i].page_num,
						COL_ICON,icon,
						COL_TEXT,_("Fcitx"),
						-1);
			}
			
		}
		
		i++;
	}	
					
	return store;
}


static void
selection_cb(GtkTreeSelection *selection,
		GtkTreeModel *model)
{
	GtkTreeIter iter;
	GtkTreePath *path;
	GValue value={0,};
	
	if(!gtk_tree_selection_get_selected(selection,NULL,&iter))
		return;

	/*从 model中的COL_NUM属性得到当前选中的序号，并将值传入GValue类型的value*/
	gtk_tree_model_get_value(model,&iter,
			COL_NUM,&value);

	/*得到当前model的tree_path，再将包装进model的tree_view根据path来展开*/
	path=gtk_tree_model_get_path(model,&iter);
	gtk_tree_view_expand_row (GTK_TREE_VIEW (g_object_get_data(G_OBJECT(model),"tree_view")),path,TRUE);

	/*用get_int的方法得到value结构中的序号，并将notebook设置为指定序号的页*/
	gtk_notebook_set_current_page(GTK_NOTEBOOK(notebook),g_value_get_int(&value));

	g_value_unset(&value);
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

	g_object_set_data(G_OBJECT(model),"tree_view",tree_view);
	
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
	GtkWidget *hpaned;
	GtkWidget *button;

	gtk_window_set_default_icon_from_file(UT_LOGO,NULL);
/*创建主窗体，分别设置好窗口标题，默认尺寸，是否可调，默认放置位置，边框
 *并连接关闭的信号
 */ 
	window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
	gtk_window_set_title(GTK_WINDOW(window),"Ubuntu Tweak!");
	gtk_widget_set_size_request(GTK_WIDGET(window),650,680);
	gtk_window_set_resizable(GTK_WINDOW(window),TRUE);
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
	hpaned=gtk_hpaned_new();
	gtk_box_pack_start(GTK_BOX(vbox),hpaned,TRUE,TRUE,0);

/*创建Tree View，将其包装进scrolled_window里，再装进hbox里*/
	tree_view = create_treeview();
	scrolled_window=gtk_scrolled_window_new(NULL,NULL);
	gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(scrolled_window),
					GTK_POLICY_AUTOMATIC,
					GTK_POLICY_AUTOMATIC);
	gtk_widget_set_size_request (GTK_WIDGET(scrolled_window),150,-1);
	gtk_paned_pack1(GTK_PANED(hpaned),scrolled_window,TRUE,TRUE);
	gtk_container_add(GTK_CONTAINER(scrolled_window),tree_view);

/*创建notebook，包装进hbox里*/
	notebook=create_notebook();
	gtk_paned_pack2(GTK_PANED(hpaned),notebook,TRUE,FALSE);

/*窗体下部的hbox，用于放置几个按钮*/
	hbox=gtk_hbox_new(FALSE,5);
	gtk_box_pack_start(GTK_BOX(vbox),hbox,FALSE,FALSE,5);

	button=gtk_button_new_from_stock(GTK_STOCK_ABOUT);
	g_signal_connect((button),"clicked",G_CALLBACK(show_about),NULL);
	gtk_box_pack_start(GTK_BOX(hbox),button,FALSE,FALSE,0);

	button=gtk_button_new_from_stock(GTK_STOCK_QUIT);
	g_signal_connect(button,"clicked",G_CALLBACK(gtk_main_quit),NULL);
	gtk_box_pack_end(GTK_BOX(hbox),button,FALSE,FALSE,0);
	
	/*
	button=gtk_button_new_from_stock(GTK_STOCK_OK);
	gtk_box_pack_end(GTK_BOX(hbox),button,FALSE,FALSE,0);
	*/

	return window;
}
