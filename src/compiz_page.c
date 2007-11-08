#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"

static const gchar *keys_of_plugins_with_edge[]={
	"/apps/compiz/plugins/expo/allscreens/options/expo_edge",
	"/apps/compiz/plugins/scale/allscreens/options/initiate_edge",
	"/apps/compiz/plugins/rotate/allscreens/options/rotate_flip_left_edge",
	"/apps/compiz/plugins/rotate/allscreens/options/rotate_flip_right_edge",
};

static const gchar *names_of_plugins_with_edge[]={
	"expo",
	"initiate",
	"rotate_flip_left_edge",
	"rotate_flip_right_edge",
};
	
static GtkWidget *create_checkbutton_wobby_menu(gchar *label,gchar *key);
static GtkWidget *create_checkbutton_snap_windows(gchar *label);
static GSList	*get_active_plugins(GConfClient *client);

static void	wobby_checkbutton_toggeled(GtkWidget *checkbutton,gchar *key);
static void	snap_checkbutton_toggeled(GtkWidget *checkbutton, gpointer data);
static void	cb_combo_box_changed(GtkWidget *combobox,gchar *edge);
static void	remove_edge(gchar *keys_of_plugins_with_edge,gchar *edge);
static void	add_edge_base(gchar *keys_of_plugins_with_edge,gchar *edge);
static void	change_edge(GtkWidget *combobox,gchar *edge);
static void	add_edge(GtkWidget *combobox,gchar *edge);

GtkWidget *create_edge_combo_box(gchar *edge)
{
	GtkWidget	*combobox;
	GConfClient	*client;
	GSList		*edge_list=NULL;
	GSList		*plugins_list=NULL;
	gint		active_plugins;
	guint		length;
	gint		i;
	guint		j;

	combobox=gtk_combo_box_new_text();
	//g_object_set_data(G_OBJECT(combobox),"previous","NULL");
	gtk_combo_box_append_text(GTK_COMBO_BOX(combobox),"展示桌面");
	gtk_combo_box_append_text(GTK_COMBO_BOX(combobox),"排列窗口");
	gtk_combo_box_append_text(GTK_COMBO_BOX(combobox),"转到上一面");
	gtk_combo_box_append_text(GTK_COMBO_BOX(combobox),"转到下一面");
	gtk_combo_box_append_text(GTK_COMBO_BOX(combobox),"----");

	gtk_combo_box_set_active(GTK_COMBO_BOX(combobox),4);

	client=gconf_client_get_default();

	plugins_list=get_active_plugins(client);

	for(i=0;i<4;i++)
	{
		/*从key值中获得edge的列表*/
		edge_list=gconf_client_get_list(client,
					keys_of_plugins_with_edge[i],
					GCONF_VALUE_STRING,
					NULL);
	


		/*将获得的列表与传入的edge值进行对比，吻合则设置combobox为活动状态*/
		for(length=g_slist_length(edge_list),j=0;j<length;j++)
		{
			gchar *temp=g_slist_nth_data(edge_list,j);

			if(!g_ascii_strcasecmp(edge,temp)){

				gtk_combo_box_set_active(GTK_COMBO_BOX(combobox),i);
				g_print("稳合了%s！\n",edge);
				g_object_set_data(G_OBJECT(combobox),"previous",names_of_plugins_with_edge[i]);

				g_free(temp);
				
				break;
			}

			g_free(temp);
		} 
	}

	g_print("设置好了，现在的设定是%s！\n",g_object_get_data(G_OBJECT(combobox),"previous"));

	g_signal_connect(G_OBJECT(combobox),"changed",G_CALLBACK(cb_combo_box_changed),edge);
	
	g_slist_free(edge_list);
	g_object_unref(client);

	return combobox;
}

GtkWidget *create_compiz_page()
{
	GConfClient *client;
	gchar *wallpaper;
	GdkPixbuf *pixbuf;
	GtkWidget *main_vbox;
	GtkWidget *vbox;
	GtkWidget *hbox;
	GtkWidget *label;
	GtkWidget *snapping_checkbutton;
	GtkWidget *movewobby_checkbutton;
	GtkWidget *checkbutton;
	GtkWidget *combobox;
	GtkWidget *image;

	main_vbox=gtk_vbox_new(FALSE,10);
	gtk_widget_show(main_vbox);
	gtk_container_set_border_width(GTK_CONTAINER(main_vbox),5);

	label=gtk_label_new(NULL);
	gtk_label_set_markup(GTK_LABEL(label),_("<b>System Security options</b>"));
	gtk_misc_set_alignment(GTK_MISC(label),0,0);
	gtk_widget_show(label);
	gtk_box_pack_start(GTK_BOX(main_vbox),label,FALSE,FALSE,0);

	hbox=gtk_hbox_new(FALSE,0);
	gtk_box_pack_start(GTK_BOX(main_vbox),hbox,FALSE,FALSE,0);

	vbox=gtk_vbox_new(FALSE,0);
	gtk_box_pack_start(GTK_BOX(hbox),vbox,FALSE,FALSE,0);

	combobox=create_edge_combo_box("TopLeft");
	gtk_box_pack_start(GTK_BOX(vbox),combobox,FALSE,FALSE,0);

	combobox=create_edge_combo_box("BottomLeft");
	gtk_box_pack_end(GTK_BOX(vbox),combobox,FALSE,FALSE,0);

	client=gconf_client_get_default();
	wallpaper=gconf_client_get_string(client,
				"/desktop/gnome/background/picture_filename",
				NULL);

	if(!g_ascii_strcasecmp("",wallpaper)){
		pixbuf=gdk_pixbuf_new_from_file_at_size("/usr/share/backgrounds/warty-final-ubuntu.png",
				160,
				100,
				NULL);
			g_message("wallpaper is %s\n",wallpaper);
	}else{
		pixbuf=gdk_pixbuf_new_from_file_at_size(wallpaper,
						160,
						100,
						NULL);
	}

	image=gtk_image_new_from_pixbuf(pixbuf);
	gtk_box_pack_start(GTK_BOX(hbox),image,FALSE,FALSE,0);

	vbox=gtk_vbox_new(FALSE,0);
	gtk_box_pack_start(GTK_BOX(hbox),vbox,FALSE,FALSE,0);

	combobox=create_edge_combo_box("TopRight");
	gtk_box_pack_start(GTK_BOX(vbox),combobox,FALSE,FALSE,0);

	combobox=create_edge_combo_box("BottomRight");
	gtk_box_pack_end(GTK_BOX(vbox),combobox,FALSE,FALSE,0);

	vbox=gtk_vbox_new(FALSE,0);
	gtk_box_pack_start(GTK_BOX(main_vbox),vbox,FALSE,FALSE,0);

	snapping_checkbutton=create_checkbutton_snap_windows("开启粘性窗口");
	gtk_box_pack_start(GTK_BOX(vbox),snapping_checkbutton,TRUE,TRUE,0);

	checkbutton=create_checkbutton_wobby_menu("开启弹性菜单","/apps/compiz/plugins/wobbly/screen0/options/map_effect");
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,TRUE,TRUE,0);

	checkbutton=create_checkbutton_wobby_menu("最大化时弹性效果","/apps/compiz/plugins/wobbly/screen0/options/maximize_effect");
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,TRUE,TRUE,0);

	movewobby_checkbutton=create_checkbutton_wobby_menu("移动窗口时启用摇晃","/apps/compiz/plugins/wobbly/screen0/options/move_window_match");
	g_object_set_data(G_OBJECT(movewobby_checkbutton),"disable",snapping_checkbutton);
	gtk_box_pack_start(GTK_BOX(vbox),movewobby_checkbutton,TRUE,TRUE,0);

	vbox=gtk_vbox_new(FALSE,0);
	gtk_box_pack_start(GTK_BOX(main_vbox),vbox,FALSE,FALSE,0);

   GtkWidget *radio1, *radio2;
   
   /* Create a radio button with a GtkEntry widget */
   radio1 = gtk_radio_button_new_with_label(NULL,"使用桌面墙");
   
   /* Create a radio button with a label */
   radio2 = gtk_radio_button_new_with_label_from_widget (GTK_RADIO_BUTTON (radio1),"使用桌面立方体.");
   
   /* Pack them into a box, then show all the widgets */
   gtk_box_pack_start (GTK_BOX (vbox), radio1, TRUE, TRUE, 2);
   gtk_box_pack_start (GTK_BOX (vbox), radio2, TRUE, TRUE, 2);

	gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(radio2),TRUE);

	checkbutton=gtk_check_button_new_with_label("开启立方体倒影");
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,TRUE,TRUE,0);

	g_object_unref(client);

	return main_vbox; 
}

GtkWidget *create_checkbutton_wobby_menu(gchar *label,gchar *key)
{
	GtkWidget *checkbutton;
	GConfValue *value;
	GConfClient *client;
	GSList *list=NULL;
	gboolean bool;
	guint length,j;
	gint map_effect;

	checkbutton=gtk_check_button_new_with_label(label);
	g_signal_connect(G_OBJECT(checkbutton),"toggled",G_CALLBACK(wobby_checkbutton_toggeled),key);

	client=gconf_client_get_default();

	list=get_active_plugins(client);

	for(length=g_slist_length(list),j=0;j<length;j++)
	{
		gchar *temp=g_slist_nth_data(list,j);

		if(!g_ascii_strcasecmp("wobbly",temp)){

			GString *match;
			
			value=gconf_client_get(client,key,NULL);
			
			if(value->type==GCONF_VALUE_INT){

				map_effect=gconf_value_get_int(value);

				match=g_string_new(gconf_client_get_string(client,
					"/apps/compiz/plugins/wobbly/screen0/options/map_window_match",
					NULL));

				if(map_effect==1&&match->len>=4){

					gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),TRUE);
				}

				g_string_free(match,TRUE);
			}
			else if(value->type==GCONF_VALUE_BOOL){
				
				bool=gconf_value_get_bool(value);
				
				if(bool){
					
					gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),TRUE);
				}
			}
			else if(value->type == GCONF_VALUE_STRING){
			
				match = g_string_new(gconf_value_get_string(value));

				if(match->len>=4){
					
					gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),TRUE);
				}
			}

			g_free(temp);

			break;
		}

		g_free(temp);
	} 

	g_slist_free(list);
	g_object_unref(client);

	return checkbutton;
}

void wobby_checkbutton_toggeled(GtkWidget *checkbutton,
				gchar *key)
{
	GConfClient *client;
	GConfValue *value;
	GSList *list=NULL;
	gboolean bool;
	gint j,length;
	
	bool=gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(checkbutton));
	client=gconf_client_get_default();
	list=gconf_client_get_list(client,
			"/apps/compiz/general/allscreens/options/active_plugins",
			GCONF_VALUE_STRING,
			NULL);

	if(g_object_get_data(G_OBJECT(checkbutton),"disable")){
		g_message("哈哈！我要关掉某个选项了！\n");

		if(bool){
			gtk_widget_set_sensitive(GTK_WIDGET(g_object_get_data(G_OBJECT(checkbutton),"disable")),FALSE);

			if(gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(g_object_get_data(G_OBJECT(checkbutton),"disable")))){

				length=g_slist_length(list);

				for(j=0;j<length;j++)
				{
					gconstpointer temp=g_slist_nth_data(list,j);

					if(!g_ascii_strcasecmp("snap",temp)){

						list=g_slist_remove(list,temp);
			
						gconf_client_set_list(client,
							"/apps/compiz/general/allscreens/options/active_plugins",
							GCONF_VALUE_STRING,
							list,
							NULL);

						break;
					}

					temp=NULL;
				}
			}
		}else{
			gtk_widget_set_sensitive(GTK_WIDGET(g_object_get_data(G_OBJECT(checkbutton),"disable")),TRUE);

		}
	}

	if(bool==TRUE){
		list=g_slist_append(list,"wobbly");
		gconf_client_set_list(client,
			"/apps/compiz/general/allscreens/options/active_plugins",
			GCONF_VALUE_STRING,
			list,
			NULL);

		value=gconf_client_get(client,key,NULL);

		if(value->type==GCONF_VALUE_INT){

			gconf_client_set_int(client,key,1,NULL);
			gconf_client_set_string(client,
					"/apps/compiz/plugins/wobbly/screen0/options/map_window_match",
					"Splash | DropdownMenu | PopupMenu | Tooltip | Notification | Combo | Dnd | Unknown",NULL);

		}
		else if(value->type==GCONF_VALUE_BOOL){
			
			gconf_client_set_bool(client,key,TRUE,NULL);

		}
		else if(value->type == GCONF_VALUE_STRING){
			
			gconf_client_set_string(client,key,"Toolbar | Menu | Utility | Dialog | Normal | Unknown",NULL);
		}	
	}else{
		list=g_slist_remove(list,"wobbly");
		gconf_client_set_list(client,
			"/apps/compiz/general/allscreens/options/active_plugins",
			GCONF_VALUE_STRING,
			list,
			NULL);

		value=gconf_client_get(client,key,NULL);

		if(value->type==GCONF_VALUE_INT){

			gconf_client_set_int(client,key,0,NULL);

		}
		else if(value->type==GCONF_VALUE_BOOL){
			
			gconf_client_set_bool(client,key,FALSE,NULL);
			
		}
		else if(value->type == GCONF_VALUE_STRING){
			
			gconf_client_set_string(client,key,"",NULL);
		}	
	}

	g_slist_free(list);
	g_object_unref(client);
}

GtkWidget *create_checkbutton_snap_windows(gchar *label)
{
	GtkWidget *checkbutton;
	GConfClient *client;
	GSList *list=NULL;
	guint length,j;

	checkbutton=gtk_check_button_new_with_label(label);
	client=gconf_client_get_default();

	list=gconf_client_get_list(client,
				"/apps/compiz/general/allscreens/options/active_plugins",
				GCONF_VALUE_STRING,
				NULL);
	length=g_slist_length(list);

	for(j=0;j<length;j++)
	{
		gchar *temp=g_slist_nth_data(list,j);

		if(!g_ascii_strcasecmp("snap",temp)){

			gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),TRUE);

			break;
		}else{
			gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),FALSE);
		}

		g_free(temp);
	}

	g_signal_connect(G_OBJECT(checkbutton),"toggled",G_CALLBACK(snap_checkbutton_toggeled),NULL);

	g_slist_free(list);
	g_object_unref(client);

	return checkbutton;
}

void snap_checkbutton_toggeled(GtkWidget *checkbutton,
				gpointer data)
{
	GConfClient *client;
	GSList *list=NULL;
	gboolean bool;
	gconstpointer snap="snap";
	guint length,j;
	
	bool=gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(checkbutton));
	client=gconf_client_get_default();
	list=gconf_client_get_list(client,
			"/apps/compiz/general/allscreens/options/active_plugins",
			GCONF_VALUE_STRING,
			NULL);

	g_print("操作前的长度:%d\n",g_slist_length(list));
/*	for(j=0;j<length;j++)
	{
		gchar *temp=g_slist_nth_data(list,j);

		if(!g_ascii_strcasecmp("snap",temp)){

			gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),TRUE);
			g_print("连接信号,原来是toggled！");

			break;
		}else{
			gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),FALSE);
		}

		g_free(temp);
	} 
*/
	if(bool==TRUE){
		//g_message("你叫我开启这个插件\n");

		list=g_slist_append(list,snap);

		gconf_client_set_list(client,
			"/apps/compiz/general/allscreens/options/active_plugins",
			GCONF_VALUE_STRING,
			list,
			NULL);
	}else{
		//g_message("你叫我关闭这个插件\n");

		length=g_slist_length(list);

		for(j=0;j<length;j++)
		{
			gconstpointer temp=g_slist_nth_data(list,j);

			if(!g_ascii_strcasecmp("snap",temp)){

				list=g_slist_remove(list,temp);
			
//				g_message("the element is %s\n",temp);

				gconf_client_set_list(client,
					"/apps/compiz/general/allscreens/options/active_plugins",
					GCONF_VALUE_STRING,
					list,
					NULL);

				break;
			}

			temp=NULL;
		}
/*
		list=g_slist_remove(list,snap);

		gconf_client_set_list(client,
			"/apps/compiz/general/allscreens/options/active_plugins",
			GCONF_VALUE_STRING,
			list,
			NULL);
*/
	}

//	g_print("操作后的长度:%d\n",g_slist_length(list));
	g_slist_free(list);
	g_object_unref(client);
}

void cb_combo_box_changed(GtkWidget *combobox,gchar *edge)
{
	if(g_object_get_data(combobox,"previous")){
		g_message("先前的值是是%s,将把其删除，然后替换成新的\n",g_object_get_data(combobox,"previous"));

		change_edge(combobox,edge);
	}else{
		g_message("先前的值为空，将直接加入新的值\n");
		add_edge(combobox,edge);
	}
}

void change_edge(GtkWidget *combobox,gchar *edge)
{
	gchar *previous=g_object_get_data(combobox,"previous");

	g_print("锁定%s，开始移除....\n",previous);

	if(!g_ascii_strcasecmp("expo",previous)){
		remove_edge(keys_of_plugins_with_edge[0],edge);
		add_edge(combobox,edge);
	}
	else if(!g_ascii_strcasecmp("initiate",previous)){
		remove_edge(keys_of_plugins_with_edge[1],edge);
		add_edge(combobox,edge);
	}
	else if(!g_ascii_strcasecmp("rotate_flip_left_edge",previous)){
		remove_edge(keys_of_plugins_with_edge[2],edge);
		add_edge(combobox,edge);
	}
	else if(!g_ascii_strcasecmp("rotate_flip_right_edge",previous)){
		remove_edge(keys_of_plugins_with_edge[3],edge);
		add_edge(combobox,edge);
	}

}

void remove_edge(gchar *keys_of_plugins_with_edge,gchar *edge)
{
	GConfClient *client;
	GSList *edge_list=NULL;
	gint j,length;
	gconstpointer temp;

	client=gconf_client_get_default();
	
	edge_list=gconf_client_get_list(client,
				keys_of_plugins_with_edge,
				GCONF_VALUE_STRING,
				NULL);

	length=g_slist_length(edge_list);

		for(j=0;j<length;j++)
		{
			gconstpointer temp=g_slist_nth_data(edge_list,j);

			if(!g_ascii_strcasecmp(edge,temp)){
			
				g_message("出来了！！！\n");

				edge_list=g_slist_remove(edge_list,temp);

				gconf_client_set_list(client,
							keys_of_plugins_with_edge,
							GCONF_VALUE_STRING,
							edge_list,
							NULL);

				break;
			}

			temp=NULL;
		}

	g_object_unref(client);
	g_slist_free(edge_list);
}

void add_edge(GtkWidget *combobox,gchar *edge)
{
	int i;

	i=gtk_combo_box_get_active(GTK_COMBO_BOX(combobox));

	if(i==0){
		add_edge_base(keys_of_plugins_with_edge[0],edge);
		g_object_set_data(G_OBJECT(combobox),"previous",names_of_plugins_with_edge[0]);
	}
	else if(i==1){
		add_edge_base(keys_of_plugins_with_edge[1],edge);
		g_object_set_data(G_OBJECT(combobox),"previous",names_of_plugins_with_edge[1]);
	}
	else if(i==2){
		add_edge_base(keys_of_plugins_with_edge[2],edge);
		g_object_set_data(G_OBJECT(combobox),"previous",names_of_plugins_with_edge[2]);
	}
	else if(i==3){
		add_edge_base(keys_of_plugins_with_edge[3],edge);
		g_object_set_data(G_OBJECT(combobox),"previous",names_of_plugins_with_edge[3]);
	}
	else if(i==4){
		g_object_set_data(G_OBJECT(combobox),"previous",NULL);
	}
}

void add_edge_base(gchar *keys_of_plugins_with_edge,gchar *edge)
{
	GConfClient *client;
	GSList *edge_list=NULL;
	
	client=gconf_client_get_default();
	
	edge_list=gconf_client_get_list(client,
				keys_of_plugins_with_edge,
				GCONF_VALUE_STRING,
				NULL);
	
	edge_list=g_slist_append(edge_list,edge);

	gconf_client_set_list(client,
				keys_of_plugins_with_edge,
				GCONF_VALUE_STRING,
				edge_list,
				NULL);

	g_object_unref(client);
	g_slist_free(edge_list);
}

GSList *get_active_plugins(GConfClient *client)
{
	GSList *list=NULL;

	list=gconf_client_get_list(client,
			"/apps/compiz/general/allscreens/options/active_plugins",
			GCONF_VALUE_STRING,
			NULL);	

	return list;
}
