#ifndef _UBUNTU_TWEAK_H
#define _UBUNTU_TWEAK_H

#include <gtk/gtk.h>
#include <glib/gi18n.h>
#include <gconf/gconf-client.h>
#include <gdk-pixbuf/gdk-pixbuf.h>

typedef struct
{
	gchar *key;
	gchar *value;
}IniLine;

typedef struct
{
	gchar *filename;
	GList *lines;
	gboolean changed;
}IniFile;

IniFile *ini_file_new();

IniFile *ini_file_open_file(gchar *filename);

gboolean ini_file_write_file(IniFile *ini, gchar *filename);

void ini_file_free(IniFile *ini);

/*获取值*/
gchar *ini_file_get_value(IniFile *ini, gchar *key);

void ini_file_write_value(IniFile *ini, gchar *key, gchar *value);

GtkWidget *window;

GtkWidget *ut_checkbutton_new_with_gconf(gchar *label,gchar *key,gchar *dir,gpointer toggledata,gpointer enterdata);

GtkWidget *nt_expert_content_new_with_string(gchar *string);

GtkWidget *ut_checkbutton_new_with_string(gchar *label,gchar *key,gchar *shell,gpointer enterdata);

GtkWidget *ut_entry_new_with_gconf(gchar *key,gchar *dir,gpointer data);

void button_test(GtkWidget *widget,gpointer);

void ut_checkbutton_with_string_toggled(GtkWidget *checkbutton,gpointer data);

void ut_checkbutton_toggled(GtkWidget *checkbutton,
		gpointer data);

void ut_gconf_key_changed(GConfClient *client,guint id,GConfEntry *entry,gpointer data);

void ut_checkbutton_with_string_toggled(GtkWidget *checkbutton,gpointer data);

void _ut_entry_activated(GtkWidget *entry,
		gpointer data,
		gchar *str);

void _ut_ut_checkbutton_toggled_to_entry(GtkWidget *checkbutton,
		gpointer data,
		GtkWidget *sensitive);

void _ut_ut_checkbutton_toggled_base(GtkWidget *checkbutton,
		gpointer data,
		GtkWidget *sensitive);


#endif
