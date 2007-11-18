#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"
#include "interface.h"

void show_about(GtkWidget *widget,gpointer data)
{
	GtkWidget *dialog;

	GdkPixbuf *logo;

	static const gchar* authors[] = {
		"TualatriX <tualatrix@gmail.com>",
		NULL
	}; 

	static const gchar* artists[] = {
		"Medical-Wei <a790407@hotmail.com>",
		"m.Sharp <mac.sharp@gmail.com>",
		"taiwan ock ting <a2d8a4v@gmail.com>",
		NULL
	};

	dialog = gtk_about_dialog_new();

	logo = gdk_pixbuf_new_from_file(UT_LOGO,NULL);

	gtk_about_dialog_set_logo(GTK_ABOUT_DIALOG(dialog),logo);

	gtk_about_dialog_set_name(GTK_ABOUT_DIALOG(dialog),"Ubuntu Tweak");

	gtk_about_dialog_set_version(GTK_ABOUT_DIALOG(dialog),PACKAGE_VERSION);

	gtk_about_dialog_set_copyright(GTK_ABOUT_DIALOG(dialog),"Copyright © 2007 TualatriX");

	gtk_about_dialog_set_comments(GTK_ABOUT_DIALOG(dialog),_("Ubuntu Tweak is a tool for Ubuntu that makes it easy to configure your system and desktop settings."));

	gtk_about_dialog_set_website_label(GTK_ABOUT_DIALOG(dialog),"http://ubuntu-tweak.com");
	gtk_about_dialog_set_website(GTK_ABOUT_DIALOG(dialog),_("Nautilus Web Site"));

	gtk_about_dialog_set_authors(GTK_ABOUT_DIALOG(dialog),authors);

	gtk_about_dialog_set_artists(GTK_ABOUT_DIALOG(dialog),artists);

	gtk_about_dialog_set_translator_credits(GTK_ABOUT_DIALOG(dialog),"Super Jamie <jamie@superjamie.net>\nThree-leg-cat <threelegcat@gmail.com>");

	gtk_dialog_run(GTK_DIALOG(dialog));

	gtk_widget_destroy(dialog);

}
