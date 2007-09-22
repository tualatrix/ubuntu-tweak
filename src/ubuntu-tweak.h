#ifndef _UBUNTU_TWEAK_H

#include <gtk/gtk.h>
#include <glib/gi18n.h>
#include <gconf/gconf-client.h>
#include <gdk-pixbuf/gdk-pixbuf.h>

/*Screen size*/
gint resolution_x,resolution_y;

GtkWidget *window;

GtkWidget *create_gconf_checkbutton(gchar *label,gchar *key,gchar *dir,gpointer toggledata,gpointer enterdata);

GtkWidget *create_expert_label();

GtkWidget *create_text_checkbutton(gchar *label,gchar *key,gchar *shell,gpointer enterdata);

GtkWidget *create_gconf_entry(gchar *key,gchar *dir,gpointer data);

void button_test(GtkWidget *widget,gpointer);

void text_checkbutton_toggled(GtkWidget *checkbutton,gpointer data);

void checkbutton_toggled(GtkWidget *checkbutton,
		gpointer data);

void key_changed_callback(GConfClient *client,guint id,GConfEntry *entry,gpointer data);

void text_checkbutton_toggled(GtkWidget *checkbutton,gpointer data);

void _entry_activated(GtkWidget *entry,
		gpointer data,
		gchar *str);

void _checkbutton_toggled_entry(GtkWidget *checkbutton,
		gpointer data,
		GtkWidget *sensitive);

void _checkbutton_toggled_base(GtkWidget *checkbutton,
		gpointer data,
		GtkWidget *sensitive);

#define _UBUNTU_TWEAK_H
#endif
