#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"
#include "fcitx_page.h"

static GKeyFile *config;

static GKeyFile *load_fcitx_config();
static void save_fcitx_config(GtkWidget *widget,GKeyFile *config);

GtkWidget *ut_checkbutton_keyfile_based_new(gchar *label,gpointer method,gchar *group,gchar *key);
static void fcitx_config_set_inputmethod(GtkWidget *checkbutton,gchar *key);

GtkWidget *create_fcitx_page()
{
	
	config=load_fcitx_config();

	GtkWidget *main_vbox;
	GtkWidget *vbox;
	GtkWidget *hbox;
	GtkWidget *frame;
	GtkWidget *label;
	GtkWidget *checkbutton;
	GtkWidget *button;

	main_vbox=gtk_vbox_new(FALSE,10);
	gtk_widget_show(main_vbox);
	gtk_container_set_border_width(GTK_CONTAINER(main_vbox),10);

	label=gtk_label_new(NULL);
	gtk_label_set_markup(GTK_LABEL(label),_("<b>欢迎使用Fcitx输入法设置！</b>\n在这里，你可以禁用掉一些你并不使用的码表；\n或进行一些有关输入法行为的设置。\n未来会提供更棒的设置。"));
	gtk_misc_set_alignment(GTK_MISC(label),0,0);
	gtk_widget_show(label);
	gtk_box_pack_start(GTK_BOX(main_vbox),label,FALSE,FALSE,0);

	frame=gtk_frame_new("输入法");
	gtk_widget_show(frame);
	gtk_box_pack_start(GTK_BOX(main_vbox),frame,FALSE,FALSE,0);

	vbox=gtk_vbox_new(FALSE,10);
	gtk_widget_show(vbox);
	gtk_container_add(GTK_CONTAINER(frame),vbox);

	hbox=gtk_hbox_new(FALSE,5);
	gtk_widget_show(hbox);
	gtk_box_pack_start(GTK_BOX(vbox),hbox,FALSE,FALSE,0);
	
/*	checkbutton=create_text_checkbutton("启用仓颉",key_fcitx_table[0],g_strconcat(script_fcitx," cj",NULL),NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("启用二笔",key_fcitx_table[1],g_strconcat(script_fcitx," erbi",NULL),NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

*/
	checkbutton=ut_checkbutton_keyfile_based_new("启用双拼",fcitx_config_set_inputmethod,"输入法","启用双拼");
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	checkbutton=ut_checkbutton_keyfile_based_new("启用拼音",fcitx_config_set_inputmethod,"输入法","使用拼音");
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	checkbutton=ut_checkbutton_keyfile_based_new("启用区位",fcitx_config_set_inputmethod,"输入法","使用区位");
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);
/*
	hbox=gtk_hbox_new(FALSE,5);
	gtk_widget_show(hbox);
	gtk_box_pack_start(GTK_BOX(vbox),hbox,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("启用冰蟾全息",key_fcitx_table[4],g_strconcat(script_fcitx," qxm",NULL),NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("启用五笔拼音",key_fcitx_table[6],g_strconcat(script_fcitx," wbpy",NULL),NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("启用五笔",key_fcitx_table[7],g_strconcat(script_fcitx," wbx",NULL),NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("启用晚风",key_fcitx_table[8],g_strconcat(script_fcitx," wf",NULL),NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	vbox=gtk_vbox_new(FALSE,10);
	gtk_widget_show(vbox);
	gtk_box_pack_start(GTK_BOX(hbox),vbox,FALSE,FALSE,0);

	frame=gtk_frame_new("界面");
	gtk_widget_show(frame);
	gtk_box_pack_start(GTK_BOX(main_vbox),frame,FALSE,FALSE,0);

	vbox=gtk_vbox_new(FALSE,10);
	gtk_widget_show(vbox);
	gtk_container_add(GTK_CONTAINER(frame),vbox);

	hbox=gtk_hbox_new(FALSE,10);
	gtk_widget_show(hbox);
	gtk_box_pack_start(GTK_BOX(vbox),hbox,FALSE,FALSE,10);

	checkbutton=create_text_checkbutton("不使用时隐藏输入条",key_fcitx_apperance[0],g_strconcat(script_fcitx," banner_mode",NULL),NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("显示打字速度",key_fcitx_apperance[1],g_strconcat(script_fcitx," show_type_speed",NULL),NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);

	checkbutton=create_text_checkbutton("显示版本",key_fcitx_apperance[2],g_strconcat(script_fcitx," show_version",NULL),NULL);
	gtk_box_pack_start(GTK_BOX(hbox),checkbutton,FALSE,FALSE,0);
*/

	button=gtk_button_new_with_label("应用");
	gtk_widget_show(button);
	g_signal_connect(G_OBJECT(button),"clicked",G_CALLBACK(save_fcitx_config),config);
	gtk_box_pack_end(GTK_BOX(main_vbox),button,FALSE,FALSE,0);

	return main_vbox; 
}

GKeyFile *load_fcitx_config()
{
	GError *error = NULL;
	GKeyFile *config;

	gchar *filename, *input_buf,*output_buf;
	gsize length;
	gsize bytes_read,bytes_written;

	filename = g_build_filename (g_get_home_dir(), ".fcitx/config", NULL);

	if (!g_file_test (filename, G_FILE_TEST_EXISTS))
		g_error ("Error: File does not exist!\n");

	g_file_get_contents (filename, &input_buf, &length, &error);

	output_buf=g_convert(input_buf,
			-1,
			"UTF-8",
			"GB2312",
			&bytes_read,
			&bytes_written,
			&error);


	config=g_key_file_new();

	if(g_key_file_load_from_data(config,
				output_buf,
				-1,
				G_KEY_FILE_NONE,
				NULL))
	{
		g_print("load fcitx config successfully\n");
	}

	g_free (input_buf);
	g_free (filename);
	g_free (output_buf);

	return config;
}

void save_fcitx_config(GtkWidget *widget,GKeyFile *config)
{
	gchar *output_buf,*enddata,*filename;
	gsize length,bytes_read,bytes_written;
	GError *error=NULL;

	output_buf=g_key_file_to_data(config,
			&length,
			&error);

	enddata=g_convert(output_buf,
			-1,
			"GB2312",
			"UTF-8",
			&bytes_read,
			&bytes_written,
			&error);

	filename = g_build_filename (g_get_home_dir(), ".fcitx/config", NULL);

	if (!g_file_test (filename, G_FILE_TEST_EXISTS))
		g_error ("Error: File does not exist!\n");

	if(g_file_set_contents(filename,enddata,-1,&error))
	{
		GtkWidget *dialog;
		dialog=gtk_message_dialog_new(NULL,
					GTK_DIALOG_DESTROY_WITH_PARENT,
					GTK_MESSAGE_INFO,
					GTK_BUTTONS_OK,
					"save fcitx config successfully"
					);

		gtk_window_set_title(GTK_WINDOW(dialog),"Information");
		gtk_dialog_run(GTK_DIALOG(dialog));
		gtk_widget_destroy(dialog);
	}else{
		GtkWidget *dialog;
		dialog=gtk_message_dialog_new(NULL,
					GTK_DIALOG_DESTROY_WITH_PARENT,
					GTK_MESSAGE_INFO,
					GTK_BUTTONS_OK,
					"save fcitx config failed"
					);
		gtk_window_set_title(GTK_WINDOW(dialog),"Information");

                gtk_dialog_run(GTK_DIALOG(dialog));
                gtk_widget_destroy(dialog);
	}

	g_free (filename);
	g_free (output_buf);
	g_free (enddata);
}

GtkWidget *ut_checkbutton_keyfile_based_new(gchar *label,gpointer method,gchar *group,gchar *key)
{
	GtkWidget *checkbutton;


	checkbutton=gtk_check_button_new_with_mnemonic(label);
	gtk_widget_show(checkbutton);
	g_signal_connect(G_OBJECT(checkbutton),"toggled",G_CALLBACK(method),key);
	
	gint value;
	value=g_key_file_get_integer(config,
				group,
				key,
				NULL);	

	if(value==0){
		gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),
						FALSE);
	}else{
		gtk_toggle_button_set_active(GTK_TOGGLE_BUTTON(checkbutton),
						TRUE);
	}


	return checkbutton;
}

void fcitx_config_set_inputmethod(GtkWidget *checkbutton,gchar *key)
{
	gboolean bool;

	bool=gtk_toggle_button_get_active(GTK_TOGGLE_BUTTON(checkbutton));

	if(bool==TRUE){
		g_key_file_set_integer(config,
					"输入法",
					key,
					1);	
	}else{
		g_key_file_set_integer(config,
					"输入法",
					key,
					0);	
	}

//disable	g_free(key);
}
