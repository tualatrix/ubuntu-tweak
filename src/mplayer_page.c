#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"

static gchar *key_vo_driver="/apps/ubuntu-tweak/apps/mplayer/vo_driver";
static gchar *key_zoom="/apps/ubuntu-tweak/apps/mplayer/zoom";
static gchar *key_sub_fuzziness="/apps/ubuntu-tweak/apps/mplayer/sub-fuzziness";
static gchar *script_mplayer=PACKAGE_SCRIPTS_DIR"/ubuntu-tweak-mplayer";

GtkWidget *create_mplayer_page()
{
	GtkWidget *main_vbox;
	GtkWidget *vbox;
	GtkWidget *hbox;
	GtkWidget *label;
	GtkWidget *checkbutton;

	main_vbox=gtk_vbox_new(FALSE,5);
	gtk_widget_show(main_vbox);
	gtk_container_set_border_width(GTK_CONTAINER(main_vbox),10);

	if(g_find_program_in_path("mplayer")!=NULL){
		label=gtk_label_new(_("Here you can set mplayer"));
		gtk_misc_set_alignment(GTK_MISC(label),0,0);
		gtk_widget_show(label);
		gtk_box_pack_start(GTK_BOX(main_vbox),label,FALSE,FALSE,0);
		
		hbox=gtk_hbox_new(FALSE,10);
		gtk_widget_show(hbox);
		gtk_box_pack_start(GTK_BOX(main_vbox),hbox,FALSE,FALSE,0);

		label=gtk_label_new(" ");
		gtk_widget_show(label);
		gtk_box_pack_start(GTK_BOX(hbox),label,FALSE,FALSE,0);

		vbox=gtk_vbox_new(FALSE,10);
		gtk_widget_show(vbox);
		gtk_box_pack_start(GTK_BOX(hbox),vbox,FALSE,FALSE,0);

		checkbutton=create_text_checkbutton(_("Use X11 video driver(Recommend)"),key_vo_driver,g_strconcat(script_mplayer," vo_driver",NULL),NULL);
		gtk_widget_show(checkbutton);
		gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);

		checkbutton=create_text_checkbutton(_("Enable X11 Zoom mode(Recommend)"),key_zoom,g_strconcat(script_mplayer," zoom",NULL),NULL);
		gtk_widget_show(checkbutton);
		gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);

		checkbutton=create_text_checkbutton(_("Use smart sub-fuzziness"),key_sub_fuzziness,g_strconcat(script_mplayer," sub-fuzziness",NULL),NULL);
		gtk_widget_show(checkbutton);
		gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);
	}
	else{
		label=gtk_label_new(_("Sorry, You haven't installed Mplayer yet, Please install first."));
		gtk_misc_set_alignment(GTK_MISC(label),0,0);
		gtk_widget_show(label);
		gtk_box_pack_start(GTK_BOX(main_vbox),label,FALSE,FALSE,0);
	}

	return main_vbox; 
}
