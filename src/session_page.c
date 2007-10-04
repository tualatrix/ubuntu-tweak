#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"

static gchar *auto_save_session_char="/apps/gnome-session/options/auto_save_session";
static gchar *logout_prompt="/apps/gnome-session/options/logout_prompt";
static gchar *show_splash_screen="/apps/gnome-session/options/show_splash_screen";
static gchar *session_dir="/apps/gnome-session/options";
static gchar *splash_image="/apps/gnome-session/options/splash_image";

/*expert mode*/
GtkWidget *expander_session;
GtkWidget *expert_box_session;
GtkWidget *expert_label_session;
GtkWidget *expert_autosavesession;
GtkWidget *expert_showlogoutprompt;
GtkWidget *expert_showsplash;
GtkWidget *expert_changesplash;
gpointer present_expert_session;

GtkWidget *splash_image_button;
GdkPixbuf *new_preview;
GtkWidget *splash_image_preview;
GdkPixbuf *original_preview;

gchar *filename;
gchar *filedir;

void show_expert_label_session()
{
	if(present_expert_session!=NULL){
		gtk_widget_hide(present_expert_session);
	}
	expert_label_session=create_expert_with_string(_("Welcome! \nHere is \"Expert Mode\".If you have any question with the options, or you want to know more information about what operation will be done by the options, Just move your cursor to the option."));
	gtk_widget_show(expert_label_session);
	present_expert_session=expert_label_session;
	gtk_box_pack_start(GTK_BOX(expert_box_session),expert_label_session,TRUE,TRUE,0);
}

void expander_change_session(GtkWidget *widget,gpointer data)
{
	gboolean bool;
	bool=gtk_expander_get_expanded(GTK_EXPANDER(widget));	
	if(bool==FALSE){
		show_expert_label_session();
	}
}

GtkWidget *create_expert_autosavesession()
{
	GtkWidget *vbox;
	GtkWidget *sw;
	gchar *welcome;
	
	welcome=_("When you log in your Ubuntu, you have started a session.\nSession is the current state of your all started applications.\nSelect this option if you want the session manager to save the current state of your session.The session manager saves the session-managed applications that are open,and the settings associated with the session-managed applications. The next time that you start a session, the applications start automatically, with the saved settings.");
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

	gtk_text_buffer_set_text (buffer,welcome, -1);
	gtk_container_add(GTK_CONTAINER(sw),view);
	
	vbox=gtk_vbox_new(FALSE,0);
	gtk_widget_show(vbox);

	gtk_widget_show(view);
	gtk_box_pack_start(GTK_BOX(vbox),sw,TRUE,TRUE,0);

	g_free(welcome);

	return vbox;
}

GtkWidget *create_expert_showlogoutprompt()
{
	GtkWidget *vbox;
	GtkWidget *sw;
	gchar *welcome;
	
	welcome=_("Select this option to display a confirmation dialog when you end a session.\nIf you don't select this option, you will without a confirmation dialog when you click the \"System\"-\"Quit\".");
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
	gtk_text_buffer_set_text (buffer,welcome, -1);

	gtk_container_add(GTK_CONTAINER(sw),view);
	
	vbox=gtk_vbox_new(FALSE,0);
	gtk_widget_show(vbox);

	gtk_widget_show(view);
	gtk_box_pack_start(GTK_BOX(vbox),sw,TRUE,TRUE,0);

	g_free(welcome);

	return vbox;
}

GtkWidget *create_expert_showsplash()
{
	GtkWidget *vbox;
	GtkWidget *sw;
	gchar *welcome;
	
	welcome=_("Select this option to display a splash screen when you start a session.");
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
	gtk_text_buffer_set_text (buffer,welcome, -1);

	gtk_container_add(GTK_CONTAINER(sw),view);
	
	vbox=gtk_vbox_new(FALSE,0);
	gtk_widget_show(vbox);

	gtk_widget_show(view);
	gtk_box_pack_start(GTK_BOX(vbox),sw,TRUE,TRUE,0);

	g_free(welcome);

	return vbox;
}

GtkWidget *create_expert_changesplash()
{
	GtkWidget *vbox;
	GtkWidget *sw;
	gchar *welcome;
	
	welcome=_("Have you prepared your own splash images?\nNot yet?\n\nIt doesn't matter, Visit the http://www.gnome-look.org, and download the splash images what you like. Then click this button to choose it!");
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
	gtk_text_buffer_set_text (buffer,welcome, -1);

	gtk_container_add(GTK_CONTAINER(sw),view);
	
	vbox=gtk_vbox_new(FALSE,0);
	gtk_widget_show(vbox);

	gtk_widget_show(view);
	gtk_box_pack_start(GTK_BOX(vbox),sw,TRUE,TRUE,0);

	g_free(welcome);

	return vbox;
}

void show_expert_autosavesession(GtkWidget *widget,gpointer data)
{
	if(present_expert_session!=expert_autosavesession){
		gtk_widget_hide(present_expert_session);
		expert_autosavesession=create_expert_autosavesession();
		gtk_widget_show(expert_autosavesession);
		present_expert_session=expert_autosavesession;
		gtk_box_pack_start(GTK_BOX(expert_box_session),expert_autosavesession,FALSE,FALSE,0);
	}
}

void show_expert_showlogoutprompt(GtkWidget *widget,gpointer data)
{
	if(present_expert_session!=expert_showlogoutprompt){
		gtk_widget_hide(present_expert_session);
		expert_showlogoutprompt=create_expert_showlogoutprompt();
		gtk_widget_show(expert_showlogoutprompt);
		present_expert_session=expert_showlogoutprompt;
		gtk_box_pack_start(GTK_BOX(expert_box_session),expert_showlogoutprompt,FALSE,FALSE,0);
	}
}

void show_expert_showsplash(GtkWidget *widget,gpointer data)
{
	if(present_expert_session!=expert_showsplash){
		gtk_widget_hide(present_expert_session);
		expert_showsplash=create_expert_showsplash();
		gtk_widget_show(expert_showsplash);
		present_expert_session=expert_showsplash;
		gtk_box_pack_start(GTK_BOX(expert_box_session),expert_showsplash,FALSE,FALSE,0);
	}
}

void show_expert_changesplash(GtkWidget *widget,gpointer data)
{
	if(present_expert_session!=expert_changesplash){
		gtk_widget_hide(present_expert_session);
		expert_changesplash=create_expert_changesplash();
		gtk_widget_show(expert_changesplash);
		present_expert_session=expert_changesplash;
		gtk_box_pack_start(GTK_BOX(expert_box_session),expert_changesplash,FALSE,FALSE,0);
	}
}

void splash_select(GtkWidget *widget,gpointer data)
{
	GtkWidget *dialog;
	GConfClient *client;

	gint x,y;

	dialog=gtk_file_chooser_dialog_new(_("Choose a Splash file"),
		NULL,
		GTK_FILE_CHOOSER_ACTION_OPEN,
		GTK_STOCK_OPEN, GTK_RESPONSE_ACCEPT, GTK_STOCK_CANCEL, GTK_RESPONSE_CANCEL, NULL);
	/*在打开文件的对话框中，将当前目前设定为原文件所在目录*/
	gtk_file_chooser_set_current_folder(GTK_FILE_CHOOSER(dialog),filedir);

	if(gtk_dialog_run(GTK_DIALOG(dialog))==GTK_RESPONSE_ACCEPT){
		filename=gtk_file_chooser_get_filename(GTK_FILE_CHOOSER(dialog));
		gtk_label_set_text(GTK_LABEL(data),filename);
		original_preview=gdk_pixbuf_new_from_file(filename,NULL);
		x=gdk_pixbuf_get_width(original_preview);
		y=gdk_pixbuf_get_height(original_preview);

		new_preview=gdk_pixbuf_scale_simple(original_preview,x/2,y/2,GDK_INTERP_NEAREST);
		gtk_image_set_from_pixbuf(GTK_IMAGE(splash_image_preview),new_preview);
		client=gconf_client_get_default();
		gconf_client_set_string(client,splash_image,filename,NULL);
	}
	gtk_widget_destroy(dialog);
}

void checkbutton_toggled_splash(GtkWidget *checkbutton,
		gpointer data)
{
	_checkbutton_toggled_base(checkbutton,data,splash_image_button);
}


GtkWidget *change_splash()
{
	GtkWidget *splash_image_hbox;
	GtkWidget *splash_image_alignment;
	GtkWidget *splash_image_button_vbox;
	GtkWidget *splash_label_filename;

	gboolean bool;
	GConfClient *client;
	client=gconf_client_get_default();

	filename=gconf_client_get_string(client,splash_image,NULL);
	filedir=g_dirname(filename);

/*初次修改Splash的用户需要这段来判断位于GConf的值是否是无路径的默认Splash*/
	if(!g_ascii_strcasecmp(filedir,"splash")){
		filedir=g_strconcat("/usr/share/pixmaps/",filedir,NULL);
		filename=g_strconcat("/usr/share/pixmaps/",filename,NULL);
	}
	bool=gconf_client_get_bool(client,show_splash_screen,NULL);
/*预览图所在位置*/
	gint x,y;

	original_preview=gdk_pixbuf_new_from_file(filename,NULL);
	x=gdk_pixbuf_get_width(original_preview);
	y=gdk_pixbuf_get_height(original_preview);
	if ((x * 180 / y) > 240) {
		y = y * 240 / x;
		x = 240;
	} else {
		x = x * 180 / y;
		y = 180;
	}
	new_preview=gdk_pixbuf_scale_simple(original_preview,x,y,GDK_INTERP_NEAREST);

	splash_image_hbox=gtk_hbox_new(FALSE,0);
	gtk_widget_show(splash_image_hbox);

	splash_image_button=gtk_button_new();
	gtk_widget_show(splash_image_button);
	g_signal_connect(G_OBJECT(splash_image_button),"enter",G_CALLBACK(show_expert_changesplash),NULL);
	gtk_box_pack_start(GTK_BOX(splash_image_hbox),splash_image_button,TRUE,FALSE,20);

	if(bool==FALSE){
		gtk_widget_set_sensitive(splash_image_button,FALSE);
	}else{
		gtk_widget_set_sensitive(splash_image_button,TRUE);
	}

	splash_image_button_vbox=gtk_vbox_new(FALSE,2);
	gtk_widget_show(splash_image_button_vbox);
	gtk_container_add(GTK_CONTAINER(splash_image_button),splash_image_button_vbox);
	gtk_container_set_border_width(GTK_CONTAINER(splash_image_button_vbox),5);

	splash_image_alignment=gtk_alignment_new(0.5,0.5,1,1);
	gtk_widget_show(splash_image_alignment);
	gtk_box_pack_start(GTK_BOX(splash_image_button_vbox),splash_image_alignment,TRUE,TRUE,0);
	gtk_widget_set_size_request(splash_image_alignment,240,180);

	splash_image_preview=gtk_image_new_from_pixbuf(new_preview);
	gtk_widget_show(splash_image_preview);
	gtk_container_add(GTK_CONTAINER(splash_image_alignment),splash_image_preview);

	splash_label_filename=gtk_label_new(filename);
	gtk_widget_show(splash_label_filename);
	gtk_box_pack_end(GTK_BOX(splash_image_button_vbox),splash_label_filename,FALSE,FALSE,0);
	
	g_signal_connect(G_OBJECT(splash_image_button),"clicked",G_CALLBACK(splash_select),splash_label_filename);

	return splash_image_hbox;
}

GtkWidget *create_session_page()
{
/*Session Page*/
	GtkWidget *session_main_vbox;
	GtkWidget *session_vbox;
	GtkWidget *session_hbox;
	GtkWidget *session_vbox_right;
	GtkWidget *blank_label;
	GtkWidget *save_session_checkbutton;
	GtkWidget *display_menu_checkbutton;
	GtkWidget *display_splash_checkbutton;
	GtkWidget *splash_image_hbox;

	session_main_vbox=gtk_vbox_new(FALSE,0);
	gtk_widget_show(session_main_vbox);

	session_vbox=gtk_vbox_new(FALSE,10);
	gtk_widget_show(session_vbox);
	gtk_box_pack_start(GTK_BOX(session_main_vbox),session_vbox,FALSE,FALSE,0);
	gtk_container_set_border_width(GTK_CONTAINER(session_vbox),10);

	GtkWidget *frame;
	frame=gtk_frame_new(_("Session Control"));
	gtk_widget_show(frame);
	gtk_box_pack_start(GTK_BOX(session_vbox),frame,FALSE,FALSE,0);

	session_hbox=gtk_hbox_new(FALSE,5);
	gtk_widget_show(session_hbox);
	gtk_container_add(GTK_CONTAINER(frame),session_hbox);

	blank_label=gtk_label_new(" ");
	gtk_widget_show(blank_label);
	gtk_box_pack_start(GTK_BOX(session_hbox),blank_label,FALSE,FALSE,0);

	session_vbox_right=gtk_vbox_new(FALSE,5);
	gtk_widget_show(session_vbox_right);
	gtk_box_pack_start(GTK_BOX(session_hbox),session_vbox_right,FALSE,FALSE,0);

	save_session_checkbutton=create_gconf_checkbutton(_("Auto save session"),
		auto_save_session_char,
		session_dir,
		checkbutton_toggled,
		show_expert_autosavesession);
	gtk_widget_show(save_session_checkbutton);
	gtk_box_pack_start(GTK_BOX(session_vbox_right),save_session_checkbutton,FALSE,FALSE,0);

	display_menu_checkbutton=create_gconf_checkbutton(_("Show logout prompt"),
		logout_prompt,
		session_dir,
		checkbutton_toggled,
		show_expert_showlogoutprompt);
	gtk_widget_show(display_menu_checkbutton);
	gtk_box_pack_start(GTK_BOX(session_vbox_right),display_menu_checkbutton,FALSE,FALSE,0);

	display_splash_checkbutton=create_gconf_checkbutton(_("Show splash screen"),
		show_splash_screen,
		session_dir,
		checkbutton_toggled_splash,
		show_expert_showsplash);
	gtk_widget_show(display_splash_checkbutton);
	gtk_box_pack_start(GTK_BOX(session_vbox_right),display_splash_checkbutton,FALSE,FALSE,0);

	frame=gtk_frame_new(_("Click the big button to change splash screen"));
	gtk_widget_show(frame);
	gtk_box_pack_start(GTK_BOX(session_vbox),frame,FALSE,FALSE,0);

/*splash*/
	splash_image_hbox=change_splash();
	gtk_widget_show(splash_image_hbox);
	gtk_container_add(GTK_CONTAINER(frame),splash_image_hbox);
	gtk_widget_set_size_request(splash_image_hbox,256,-1);

/*expander*/
	expander_session=gtk_expander_new_with_mnemonic(_("Need some help? Click here!"));
	gtk_widget_show(expander_session);
	g_signal_connect(G_OBJECT(expander_session),"activate",G_CALLBACK(expander_change_session),NULL);
	gtk_box_pack_start(GTK_BOX(session_vbox),expander_session,FALSE,FALSE,0);

	expert_box_session=gtk_vbox_new(FALSE,0);
	gtk_widget_set_size_request(GTK_WIDGET(expert_box_session),200,100);
	gtk_widget_show(expert_box_session);
	gtk_container_add(GTK_CONTAINER(expander_session),expert_box_session);

	return session_main_vbox;
}
