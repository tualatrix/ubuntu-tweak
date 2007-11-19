#include "ubuntu-tweak.h"

GtkWidget *nt_expert_content_new_with_string(gchar *string)
{
	GtkWidget *vbox;
	GtkWidget *sw;

	sw=gtk_scrolled_window_new (NULL, NULL);
	gtk_widget_show(sw);
	gtk_scrolled_window_set_policy (GTK_SCROLLED_WINDOW (sw),
			      GTK_POLICY_AUTOMATIC,
			      GTK_POLICY_AUTOMATIC);

	GtkWidget *view;
	GtkTextBuffer *buffer;

	view=gtk_text_view_new ();
	gtk_text_view_set_wrap_mode(GTK_TEXT_VIEW(view),GTK_WRAP_WORD);
	gtk_text_view_set_editable(GTK_TEXT_VIEW(view),FALSE);
	gtk_widget_show(view);
	buffer = gtk_text_view_get_buffer (GTK_TEXT_VIEW (view));

	gtk_text_buffer_set_text (buffer,string, -1);

	gtk_container_add(GTK_CONTAINER(sw),view);
	
	vbox=gtk_vbox_new(FALSE,0);
	gtk_widget_show(vbox);

	gtk_widget_show(view);
	gtk_box_pack_start(GTK_BOX(vbox),sw,TRUE,TRUE,0);

	return vbox;	
}

void ut_gconf_key_changed(GConfClient *client,guint id,GConfEntry *entry,gpointer data)
{
	GtkWidget *checkbutton;
	GConfValue *value;
	gboolean bool;
	
	value=gconf_entry_get_value(entry);
	checkbutton=GTK_WIDGET(data);
	
	if(value==NULL){
		gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),FALSE);
	}else{
		if(value->type==GCONF_VALUE_STRING){
				gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),TRUE);
		}else if(value->type==GCONF_VALUE_BOOL){
				if((bool=gconf_value_get_bool(value))==TRUE){
					gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),TRUE);
				}else{
					gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),FALSE);
			}
		}
	}
}

/*核心API之一，创建带gconf监视功能的checkbutton按钮
 * 传入参数为，label──按钮的标签
 * 		key──要求监视的键值
 * 		dir──监视的key目录
 * 		toggledata──这个指针在开关按钮时启用
 * 		enterdata──用于开起专家模式，或者用于其他功能
*/
GtkWidget *ut_checkbutton_new_with_gconf(gchar *label,gchar *key,gchar *dir,gpointer toggledata,gpointer enterdata)
{
	GtkWidget *checkbutton;
	GConfValue *value;
	GConfClient *client;
	gboolean bool;

	client=gconf_client_get_default();
	value=gconf_client_get(client,key,NULL);

	checkbutton=gtk_check_button_new_with_mnemonic(label);
	gtk_widget_show(checkbutton);
	g_signal_connect(G_OBJECT(checkbutton),"toggled",G_CALLBACK(toggledata),key);
	if(enterdata!=NULL){
		g_signal_connect(G_OBJECT(checkbutton),"enter",G_CALLBACK(enterdata),NULL);
	}

	if(value==NULL){
		gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),FALSE);
	}else{
		if(value->type==GCONF_VALUE_STRING){
			gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),TRUE);
		}
		else if(value->type==GCONF_VALUE_INT){
			gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),FALSE);
		}
		else if(value->type==GCONF_VALUE_BOOL){
			bool=gconf_client_get_bool(client,key,NULL);
			if(bool==TRUE){
				gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),TRUE);
			}else{
				gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),FALSE);
			}
		}
	}

	gconf_client_add_dir(client,
		dir,
		GCONF_CLIENT_PRELOAD_NONE,
		NULL);
	gconf_client_notify_add(client,
		key,
		ut_gconf_key_changed,
		checkbutton,
		NULL,NULL);

	g_object_unref(client);

	return checkbutton;
}
/*核心API之一，创建用于修改配置文件基于文本的按钮，其中shell是创建时执行的命令,虽然它是基于文本的，但是还是通过监视自创的键值，以方便调用*/
GtkWidget *ut_checkbutton_new_with_string(gchar *label,gchar *key,gchar *shell,gpointer enterdata)
{
	GtkWidget *checkbutton;
	GConfValue *value;
	GConfClient *client;
	gboolean bool;

	gchar *newshell=g_strconcat("bash ",shell,NULL);

	checkbutton=gtk_check_button_new_with_mnemonic(label);
	gtk_widget_show(checkbutton);

	client=gconf_client_get_default();
	value=gconf_client_get(client,key,NULL);

	if(value==NULL){
		gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),FALSE);
	}else{
		if(value->type==GCONF_VALUE_STRING){
			gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),TRUE);
		}
		else if(value->type==GCONF_VALUE_INT){
			gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),FALSE);
		}
		else if(value->type==GCONF_VALUE_BOOL){
			bool=gconf_client_get_bool(client,key,NULL);
			if(bool==TRUE){
				gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),TRUE);
			}else{
				gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),FALSE);
			}
		}
	}

	g_signal_connect(G_OBJECT(checkbutton),"toggled",G_CALLBACK(ut_checkbutton_with_string_toggled),newshell);

	g_free(newshell);

	g_object_unref(client);

	return checkbutton;
}

void ut_checkbutton_with_string_toggled(GtkWidget *checkbutton,gpointer data)
{
	GError *error;
	gchar *newshell;
	gboolean bool;

	bool=gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(checkbutton));
	if(bool==FALSE){
		newshell=g_strconcat(data," off",NULL);
		g_print("%s\n",newshell);		
		g_spawn_command_line_async(newshell,&error);
		gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),FALSE);
	}else{
		newshell=g_strconcat(data," on",NULL);
		g_print("%s\n",newshell);	
		g_spawn_command_line_async(newshell,&error);
		gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),TRUE);
	}

	g_free(newshell);
}

GtkWidget *ut_entry_new_with_gconf(gchar *key,gchar *dir,gpointer data)
{
/*定义键值监视事件*/
	GtkWidget *entry;
	GConfClient *client;
	gchar *str;

	client=gconf_client_get_default();
	entry=gtk_entry_new();
	gtk_widget_show(entry);

	str=gconf_client_get_string(client,key,NULL);
		
	g_signal_connect(G_OBJECT(entry),"activate",G_CALLBACK(data),key);
	if(str!=NULL){
		gtk_entry_set_text(GTK_ENTRY(entry),str);
	}else{
		gtk_entry_set_text(GTK_ENTRY(entry),_("Unset"));
	}
	gconf_client_add_dir(client,
		dir,
		GCONF_CLIENT_PRELOAD_NONE,
		NULL);
/*	gconf_client_notify_add(client,
		key,
		ut_gconf_key_changed_str,
		entry,
		NULL,NULL);
*/

	g_object_unref(client);

	g_free(str);

	return entry;
}
void _ut_ut_checkbutton_toggled_base(GtkWidget *checkbutton,
		gpointer data,
		GtkWidget *sensitive)
{
	GConfClient *client;
	gboolean bool;

	client=gconf_client_get_default();
	bool=gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(checkbutton));

	if(bool==TRUE){
		gconf_client_set_bool(client,data,TRUE,NULL);
		if(sensitive!=NULL){
			gtk_widget_set_sensitive(sensitive,TRUE);
		}
	}else{
		gconf_client_set_bool(client,data,FALSE,NULL);
		if(sensitive!=NULL){
			gtk_widget_set_sensitive(sensitive,FALSE);
		}
	}

	g_object_unref(client);
}

/*下面的指针data是经第三方传入的key*/
void _ut_ut_checkbutton_toggled_to_entry(GtkWidget *checkbutton,
		gpointer data,
		GtkWidget *sensitive)
{
	GConfClient *client;
	gboolean bool;
	
	client=gconf_client_get_default();
	bool=gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(checkbutton));

	if(bool==TRUE){
		if(sensitive!=NULL){
			gtk_widget_set_sensitive(sensitive,TRUE);
		}
	}else{
		if(sensitive!=NULL){
			gtk_entry_set_text(GTK_ENTRY(sensitive),_("Unset"));
			gconf_client_unset(client,data,NULL);
			gtk_widget_set_sensitive(sensitive,FALSE);
		}
	}

	g_object_unref(client);

}

void ut_checkbutton_toggled(GtkWidget *checkbutton,
		gpointer data)
{
	_ut_ut_checkbutton_toggled_base(checkbutton,data,NULL);
}
void _ut_entry_activated(GtkWidget *entry,
		gpointer data,
		gchar *str)
{
	GConfClient *client;
	gchar *key;
	key=data;

	client=gconf_client_get_default();

	str = gtk_editable_get_chars(GTK_EDITABLE(entry), 0, -1);

	gconf_client_set_string(client,key,
	                str, NULL);

	g_free(key);
	
	g_object_unref(client);
}

/* 从这行开始是全新的配置文件读取API
 * 用于未来的的有关系统选项的读取和写入
 * 目前为止还在测试阶段
 * 只有读取和写入功能
 * 没有新增和删除功能
 * 
*/

/*创建键值对应的行*/
static IniLine
*ini_file_create_key_line (IniFile *ini, gchar *key, gchar *value)
{
	IniLine *line;
	line  = g_malloc0 (sizeof (IniLine));
	line->key = g_strstrip (g_strdup (key));
	line->value = g_strstrip (g_strdup (value));
	ini->lines = g_list_append (ini->lines, line);

	return line;
}

/*创建空行或注释行*/
static IniLine
*ini_file_create_comment_line (IniFile *ini, gchar *key)
{
	IniLine *line;
	line  = g_malloc0 (sizeof (IniLine));
	line->key = key;
	line->value = NULL;
	ini->lines = g_list_append (ini->lines, line);

	return line;
}

/*以Key来查找行，并返回行*/
static IniLine
*ini_file_find_key(IniFile *ini, gchar *key)
{
	IniLine *line;
	GList *list;
	list=ini->lines;
	while (list)
	{
		line = (IniLine *) list->data;
		if (!g_ascii_strcasecmp (line->key, key))
		{
			return line;
		}		
		list = g_list_next (list);
	}

	return NULL;
}

/*以Key来查找行，并返回值*/
gchar *ini_file_get_value(IniFile *ini, gchar *key)
{
	IniLine *line;
	GList *list;
	list=ini->lines;
	while (list)
	{
		line = (IniLine *) list->data;
		if (!g_ascii_strcasecmp (line->key, key))
		{
			return line->value;
		}		
		list = g_list_next (list);
	}

	return NULL;
}

void ini_file_write_value(IniFile *ini, gchar *key, gchar *value)
{
	IniLine *real_line;
	ini->changed = TRUE;
	real_line = ini_file_find_key (ini, key);
	real_line->value = g_strdup(value);
}

/*创建一个ini文件类型*/
IniFile *ini_file_new()
{
	IniFile *ini;
	ini = g_malloc0(sizeof(IniFile));
	
	return ini;
}

/*创建并打开一个ini文件类型*/
IniFile *ini_file_open_file(gchar *filename)
{
	IniFile *ini;
	gchar *buffer,**lines,**key_and_value;
	gint i,j;
	gsize length;

	g_file_get_contents (filename,
			&buffer,
			&length,
			NULL);
			
	ini = g_malloc0(sizeof (IniFile));
	ini->filename = g_strdup (filename);
	ini->changed = FALSE;
	lines = g_strsplit (buffer, "\n", 0);
	g_free(buffer);
	i = 0;

	while (lines[i])
	{
		j=i+1;

		if (lines[i][0] != '#' && lines[i][0] != '\0')
		{
			key_and_value = g_strsplit (lines[i], "=", 0);
			ini_file_create_key_line (ini, key_and_value[0], key_and_value[1]);
	//		g_print("key is %s, value is %s\n",key_and_value[0],key_and_value[1]);
		}
		else if (lines[i][0] == '#' || lines[i][0] == '\0')
		{
	//		g_print("comment is %s\n", g_strdup (lines[i]));
			ini_file_create_comment_line (ini, g_strdup (lines[i]));
		}	

		i++;
	}

	g_strfreev(lines);
	return ini;
}

/*将ini文件类型写入硬盘上指定文件名的文件中去*/
gboolean ini_file_write_file(IniFile *ini, gchar *filename)
{
	GIOChannel *gio;
	GList *line_list;
	gchar *buf=NULL;
	IniLine *line;
	line_list = ini->lines;

	gio=g_io_channel_unix_new(0);
	g_io_channel_init(gio);
	gio=g_io_channel_new_file(filename,"w",NULL);
	
	while (line_list)
	{
		line = (IniLine *) line_list->data;
		if (line)
		{
			if (line->value)
			{
				g_sprintf(buf, "%s=%s\n", line->key, line->value);
			}
			else
			{
				g_sprintf(buf, "%s\n", line->key);
			}	

			g_io_channel_write_chars (gio,
						buf,
						-1,
						NULL,
						NULL);
		}
		line_list = g_list_next (line_list);
	}

	g_io_channel_shutdown(gio,TRUE,NULL);
	g_io_channel_unref(gio);
	g_free(buf);
	return TRUE;
}
			
/*释放ini文件类型占用的内存空间*/
void ini_file_free(IniFile *ini)
{
	IniLine *line;
	GList *line_list;
	g_free (ini->filename);
	line_list=ini->lines;

	while (line_list)
	{
		line=(IniLine *) line_list->data;
		g_free (line->key);
		g_free (line->value);
		g_free (line);
		line_list = g_list_next (line_list);
	}

	g_list_free(ini->lines);
	ini->lines=NULL;
	ini->filename=NULL;
}

