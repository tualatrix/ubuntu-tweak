#include "ubuntu-tweak.h"

void key_changed_callback(GConfClient *client,guint id,GConfEntry *entry,gpointer data)
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

/*核心API之一，创建带gconf监视功能的checkbutton按钮，传入参数为，label──按钮的标签，key──要求监视的键值
	dir──监视的key目录，toggledata──这个指针在开关按钮时启用，enterdata──用于开起专家模式，或者用于其他功能
*/
GtkWidget *create_gconf_checkbutton(gchar *label,gchar *key,gchar *dir,gpointer toggledata,gpointer enterdata)
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
		g_signal_connect(G_OBJECT(checkbutton),"enter",G_CALLBACK(enterdata),key);
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
		key_changed_callback,
		checkbutton,
		NULL,NULL);

	return checkbutton;
}
/*核心API之一，创建用于修改配置文件基于文本的按钮，其中shell是创建时执行的命令,虽然它是基于文本的，但是还是通过监视自创的键值，以方便调用*/
GtkWidget *create_text_checkbutton(gchar *label,gchar *key,gchar *shell,gpointer enterdata)
{
	GError *error;
	GtkWidget *checkbutton;
	GConfValue *value;
	GConfClient *client;
	gboolean bool;

	gchar *newshell=g_strconcat("bash ",shell,NULL);

	checkbutton=gtk_check_button_new_with_mnemonic(label);
	g_signal_connect(G_OBJECT(checkbutton),"toggled",G_CALLBACK(text_checkbutton_toggled),newshell);
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

	return checkbutton;
}

void text_checkbutton_toggled(GtkWidget *checkbutton,gpointer data)
{
	GError *error;
	/*gboolean bool;

	g_print("OK?");
	bool=gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(checkbutton));
	if(bool==TRUE){
		gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),FALSE);
	}else{
		gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),TRUE);
	}*/
	g_spawn_command_line_async(data,&error);
}

GtkWidget *create_gconf_entry(gchar *key,gchar *dir,gpointer data)
{
/*定义键值监视事件*/
	GtkWidget *entry;
	GConfClient *client;
	gboolean bool;
	gchar *str;

	client=gconf_client_get_default();
	entry=gtk_entry_new();
	gtk_widget_show(entry);

	str=gconf_client_get_string(client,key,NULL);
		
	g_signal_connect(G_OBJECT(entry),"activate",G_CALLBACK(data),key);
	if(str!=NULL){
		gtk_entry_set_text(GTK_ENTRY(entry),str);
	}else{
		gtk_entry_set_text(GTK_ENTRY(entry),"未设置");
	}
	gconf_client_add_dir(client,
		dir,
		GCONF_CLIENT_PRELOAD_NONE,
		NULL);
/*	gconf_client_notify_add(client,
		key,
		key_changed_callback_str,
		entry,
		NULL,NULL);
*/
	return entry;
}
void _checkbutton_toggled_base(GtkWidget *checkbutton,
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
}

/*下面的指针data是经第三方传入的key*/
void _checkbutton_toggled_entry(GtkWidget *checkbutton,
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
			gtk_entry_set_text(GTK_ENTRY(sensitive),"未设置");
			gconf_client_unset(client,data,NULL);
			gtk_widget_set_sensitive(sensitive,FALSE);
		}
	}
}
void checkbutton_toggled(GtkWidget *checkbutton,
		gpointer data)
{
	_checkbutton_toggled_base(checkbutton,data,NULL);
}
void _entry_activated(GtkWidget *entry,
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

}
