#ifndef _UBUNTU_TWEAK_H
#define _UBUNTU_TWEAK_H

#include <gtk/gtk.h>
#include <glib/gi18n.h>
#include <gconf/gconf-client.h>
#include <gdk-pixbuf/gdk-pixbuf.h>

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
