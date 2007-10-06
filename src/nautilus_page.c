#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"

static gchar *key_show_advanced_permissions="/apps/nautilus/preferences/show_advanced_permissions";
static gchar *key_burnproof="/apps/nautilus-cd-burner/burnproof";
static gchar *key_overburn="/apps/nautilus-cd-burner/overburn";
static gchar *key_nautilus_dir="/apps/nautilus/preferences";
static gchar *key_cd_burner_dir="/apps/nautilus-cd-burner";

static gchar *image_nautilus_file_permissions=PACKAGE_PIXMAPS_DIR"/nautilus-file-permissions.png";
static gchar *image_nautilus_file_advanced_permissions=PACKAGE_PIXMAPS_DIR"/nautilus-file-advanced-permissions.png";

/*expert mode*/
GtkWidget *expander_nautilus;
GtkWidget *expert_label_nautilus;
GtkWidget *expert_box_nautilus;
GtkWidget *expert_showadvancedpermissions;
GtkWidget *expert_burnproof;
GtkWidget *expert_overburn;
gpointer present_expert_nautilus;

void show_expert_label_nautilus()
{
	if(present_expert_nautilus!=NULL){
		gtk_widget_hide(present_expert_nautilus);
	}
	expert_label_nautilus=create_expert_with_string(_("Within this menu are advanced Nautilus settings. If you require more information about a specific option, move your cursor over that option, and a description will appear here."));
	gtk_widget_show(expert_label_nautilus);
	present_expert_nautilus=expert_label_nautilus;
	gtk_box_pack_start(GTK_BOX(expert_box_nautilus),expert_label_nautilus,TRUE,TRUE,0);
}

void expander_change_nautilus(GtkWidget *widget,gpointer data)
{
	gboolean bool;
	bool=gtk_expander_get_expanded(GTK_EXPANDER(widget));	
	if(bool==FALSE){
		show_expert_label_nautilus();
	}
}

GtkWidget *create_expert_showadvancedpermissions()
{
	GtkWidget *vbox;
	GtkWidget *sw;
	gchar *p1,*p2;
	
	p1=_("With default Permissions (this option unticked), the \"Permission\" tab of File or Folder Properties is like this:\n");
	p2=_("\nWith advanced Permissions (this option ticked), the \"Permission\" tab of File or Folder Properties is like this:\n");
	sw=gtk_scrolled_window_new (NULL, NULL);
	gtk_widget_show(sw);
	gtk_scrolled_window_set_policy (GTK_SCROLLED_WINDOW (sw),
			      GTK_POLICY_AUTOMATIC,
			      GTK_POLICY_AUTOMATIC);

	GtkWidget *view;
	GtkTextIter start,end;
	GtkTextBuffer *buffer;
	GdkPixbuf *pixbuf;
	view=gtk_text_view_new ();
	gtk_text_view_set_wrap_mode(GTK_TEXT_VIEW(view),GTK_WRAP_WORD);
	gtk_text_view_set_editable(GTK_TEXT_VIEW(view),FALSE);
	gtk_widget_show(view);
	buffer = gtk_text_view_get_buffer (GTK_TEXT_VIEW (view));
	pixbuf=gdk_pixbuf_new_from_file(image_nautilus_file_permissions,NULL);
	gtk_text_buffer_set_text (buffer,p1, -1);
	gtk_text_buffer_get_bounds(GTK_TEXT_BUFFER(buffer),&start,&end);
	gtk_text_buffer_insert_pixbuf(buffer,&end,pixbuf);
	gtk_text_buffer_get_bounds(GTK_TEXT_BUFFER(buffer),&start,&end);
	gtk_text_buffer_insert(GTK_TEXT_BUFFER(buffer),&end,p2,-1);
	pixbuf=gdk_pixbuf_new_from_file(image_nautilus_file_advanced_permissions,NULL);
	gtk_text_buffer_get_bounds(GTK_TEXT_BUFFER(buffer),&start,&end);
	gtk_text_buffer_insert_pixbuf(buffer,&end,pixbuf);

	gtk_container_add(GTK_CONTAINER(sw),view);
	
	vbox=gtk_vbox_new(FALSE,0);
	gtk_widget_show(vbox);
	
	gtk_widget_show(view);
	gtk_box_pack_start(GTK_BOX(vbox),sw,TRUE,TRUE,0);

	return vbox;
}

void show_expert_showadvancedpermissions(GtkWidget *widget,gpointer data)
{
	if(present_expert_nautilus!=expert_showadvancedpermissions){
		gtk_widget_hide(present_expert_nautilus);
		expert_showadvancedpermissions=create_expert_showadvancedpermissions();
		gtk_widget_show(expert_showadvancedpermissions);
		present_expert_nautilus=expert_showadvancedpermissions;
		gtk_box_pack_start(GTK_BOX(expert_box_nautilus),expert_showadvancedpermissions,FALSE,FALSE,0);
	}
}

void show_expert_burnproof(GtkWidget *widget,gpointer data)
{
	if(present_expert_nautilus!=expert_burnproof){
		gtk_widget_hide(present_expert_nautilus);
		expert_burnproof=create_expert_with_string(_("BurnProof is a technology to prevent Buffer Under Run errors when writing CDs and DVDs.\nSelect this option to enable BurnProof when writing CDs and DVDs.\nYour burner must support the BurnProof function for this to have an effect."));
		gtk_widget_show(expert_burnproof);
		present_expert_nautilus=expert_burnproof;
		gtk_box_pack_start(GTK_BOX(expert_box_nautilus),expert_burnproof,FALSE,FALSE,0);
	}
}

void show_expert_overburn(GtkWidget *widget,gpointer data)
{
	if(present_expert_nautilus!=expert_overburn){
		gtk_widget_hide(present_expert_nautilus);
		expert_overburn=create_expert_with_string(_("WARNING: You can damage your CDRW by using this incorrectly. This option is NOT recommended!\n\nOverBurn is a method of fitting more data onto a CD-R than is ordinarily permitted.\nThe maximum amount of data any given CD can hold depends on the brand and type of media, as well as your model of CD drive.\nSelect this option to enable OverBurn."));
		gtk_widget_show(expert_overburn);
		present_expert_nautilus=expert_overburn;
		gtk_box_pack_start(GTK_BOX(expert_box_nautilus),expert_overburn,FALSE,FALSE,0);
	}
}

GtkWidget *create_nautilus_page()
{
	GtkWidget *main_vbox;
	GtkWidget *vbox;
	GtkWidget *label;
	GtkWidget *checkbutton;

	main_vbox=gtk_vbox_new(FALSE,5);
	gtk_widget_show(main_vbox);
	gtk_container_set_border_width(GTK_CONTAINER(main_vbox),5);

	label=gtk_label_new(NULL);
	gtk_label_set_markup(GTK_LABEL(label),_("<b>Setting for Nautilus behavior</b>"));
	gtk_misc_set_alignment(GTK_MISC(label),0,0);
	gtk_widget_show(label);
	gtk_box_pack_start(GTK_BOX(main_vbox),label,FALSE,FALSE,0);
	
	GtkWidget *frame;
	frame=gtk_frame_new(_("File Browser"));
	gtk_widget_show(frame);
	gtk_box_pack_start(GTK_BOX(main_vbox),frame,FALSE,FALSE,0);

	checkbutton=create_gconf_checkbutton(_("Show advanced Permissions on File and Folder Property pages"),key_show_advanced_permissions,key_nautilus_dir,checkbutton_toggled,show_expert_showadvancedpermissions);
	gtk_widget_show(checkbutton);
	gtk_container_add(GTK_CONTAINER(frame),checkbutton);

	frame=gtk_frame_new(_("CD Burner"));
	gtk_widget_show(frame);
	gtk_box_pack_start(GTK_BOX(main_vbox),frame,FALSE,FALSE,0);
	
	vbox=gtk_vbox_new(FALSE,0);
	gtk_widget_show(vbox);
	gtk_container_add(GTK_CONTAINER(frame),vbox);

	checkbutton=create_gconf_checkbutton(_("Enable BurnProof technology"),key_burnproof,key_cd_burner_dir,checkbutton_toggled,show_expert_burnproof);
	gtk_widget_show(checkbutton);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_gconf_checkbutton(_("Enable OverBurn"),key_overburn,key_cd_burner_dir,checkbutton_toggled,show_expert_overburn);
	gtk_widget_show(checkbutton);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);

/*expander*/
	expander_nautilus=gtk_expander_new_with_mnemonic(_("Need some help? Click here!"));
	gtk_widget_show(expander_nautilus);
	g_signal_connect(G_OBJECT(expander_nautilus),"activate",G_CALLBACK(expander_change_nautilus),NULL);
	gtk_box_pack_end(GTK_BOX(main_vbox),expander_nautilus,FALSE,FALSE,0);

	expert_box_nautilus=gtk_vbox_new(FALSE,0);
	gtk_widget_set_size_request(GTK_WIDGET(expert_box_nautilus),200,100);
	gtk_widget_show(expert_box_nautilus);
	gtk_container_add(GTK_CONTAINER(expander_nautilus),expert_box_nautilus);

	return main_vbox; 
}
