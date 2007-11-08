#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "ubuntu-tweak.h"

static gchar *powermanager_dir="/apps/gnome-power-manager";
static gchar *key_can_hibernate="/apps/gnome-power-manager/can_hibernate";
static gchar *key_can_suspend="/apps/gnome-power-manager/can_suspend";
static gchar *key_show_cpufreq_ui="/apps/gnome-power-manager/show_cpufreq_ui";
static gchar *key_cpufreq_ac_policy="/apps/gnome-power-manager/cpufreq_ac_policy";
static gchar *key_cpufreq_battery_policy="/apps/gnome-power-manager/cpufreq_battery_policy";
static gchar *key_display_icon_policy="/apps/gnome-power-manager/display_icon_policy";

void powermanager_changed(GtkWidget *widget,gpointer data)
{
	gchar *str;
	GConfClient *client;

	client=gconf_client_get_default();
	str=gtk_combo_box_get_active_text(GTK_COMBO_BOX(widget));
	if(!strcmp(str,"On Demand")){
		gconf_client_set_string(client,
					data,
					"ondemand",
					NULL);
	}
	else if(!strcmp(str,"Power Save")){
		gconf_client_set_string(client,
				data,
				"powersave",
				NULL);
	}
	else if(!strcmp(str,"Performance")){
		gconf_client_set_string(client,
				data,
				"performance",
				NULL);
	}
	else if(!strcmp(str,"Never display")){
		gconf_client_set_string(client,
				data,
				"never",
				NULL);
	}
	else if(!strcmp(str,"Only when using battery charge")){
		gconf_client_set_string(client,
				data,
				"charge",
				NULL);
	}
	else if(!strcmp(str,"Always display")){
		gconf_client_set_string(client,
				data,
				"always",
				NULL);
	}
	g_free(str);
}

GtkWidget *create_powermanager_page()
{
	GtkWidget *main_vbox;
	GtkWidget *vbox;
	GtkWidget *hbox;
	GtkWidget *label;
	GtkWidget *checkbutton;
	GtkWidget *combobox;

	GConfClient *client;
	client=gconf_client_get_default();

	main_vbox=gtk_vbox_new(FALSE,5);
	gtk_widget_show(main_vbox);
	gtk_container_set_border_width(GTK_CONTAINER(main_vbox),5);

	label=gtk_label_new(NULL);
	gtk_label_set_markup(GTK_LABEL(label),_("<b>Advanced Power Management Settings</b>"));
	gtk_misc_set_alignment(GTK_MISC(label),0,0);
	gtk_widget_show(label);
	gtk_box_pack_start(GTK_BOX(main_vbox),label,FALSE,FALSE,0);

	hbox=gtk_hbox_new(FALSE,5);
	gtk_widget_show(hbox);
	gtk_box_pack_start(GTK_BOX(main_vbox),hbox,FALSE,FALSE,0);

	label=gtk_label_new(" ");
	gtk_widget_show(label);
	gtk_box_pack_start(GTK_BOX(hbox),label,FALSE,FALSE,0);

	vbox=gtk_vbox_new(FALSE,5);
	gtk_widget_show(vbox);
	gtk_box_pack_start(GTK_BOX(hbox),vbox,FALSE,FALSE,0);

	checkbutton=ut_checkbutton_new_with_gconf(_("Enable Hibernation"),key_can_hibernate,powermanager_dir,ut_checkbutton_toggled,NULL);
	gtk_widget_show(checkbutton);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);

	checkbutton=ut_checkbutton_new_with_gconf(_("Enable Suspend"),key_can_suspend,powermanager_dir,ut_checkbutton_toggled,NULL);
	gtk_widget_show(checkbutton);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);

	checkbutton=ut_checkbutton_new_with_gconf(_("Show CPU frequency option in \"System - Preferences - Power Management\""),key_show_cpufreq_ui,powermanager_dir,ut_checkbutton_toggled,NULL);
	gtk_widget_show(checkbutton);
	gtk_box_pack_start(GTK_BOX(vbox),checkbutton,FALSE,FALSE,0);

/*通知区域图标的显示行为*/

	hbox=gtk_hbox_new(FALSE,10);
	gtk_widget_show(hbox);
	gtk_box_pack_start(GTK_BOX(vbox),hbox,FALSE,FALSE,0);

	label=gtk_label_new(_("\"Notification Area\" Power Management icon"));
	gtk_widget_show(label);
	gtk_box_pack_start(GTK_BOX(hbox),label,FALSE,FALSE,0);

	combobox=gtk_combo_box_new_text();
	gtk_widget_show(combobox);
	gtk_box_pack_end(GTK_BOX(hbox),combobox,FALSE,FALSE,0);

	g_signal_connect(G_OBJECT(combobox),"changed",G_CALLBACK(powermanager_changed),key_display_icon_policy);

	gtk_combo_box_append_text(GTK_COMBO_BOX(combobox),_("Never display"));
	gtk_combo_box_append_text(GTK_COMBO_BOX(combobox),_("Only when using battery charge"));
	gtk_combo_box_append_text(GTK_COMBO_BOX(combobox),_("Always display"));

	if(!g_ascii_strncasecmp(gconf_client_get_string(client,key_display_icon_policy,NULL),"never",5)){
		gtk_combo_box_set_active(GTK_COMBO_BOX(combobox),0);
	}
	else if(!g_ascii_strncasecmp(gconf_client_get_string(client,key_display_icon_policy,NULL),"charge",6)){
		gtk_combo_box_set_active(GTK_COMBO_BOX(combobox),1);
	}
	else if(!g_ascii_strncasecmp(gconf_client_get_string(client,key_display_icon_policy,NULL),"always",6)){
		gtk_combo_box_set_active(GTK_COMBO_BOX(combobox),2);
	}

/*当使用交流电时，CPU的使用策略*/
	hbox=gtk_hbox_new(FALSE,10);
	gtk_widget_show(hbox);
	gtk_box_pack_start(GTK_BOX(vbox),hbox,FALSE,FALSE,0);

	label=gtk_label_new(_("When using AC power, CPU frequency policy is:"));
	gtk_widget_show(label);
	gtk_box_pack_start(GTK_BOX(hbox),label,FALSE,FALSE,0);

	combobox=gtk_combo_box_new_text();
	gtk_widget_show(combobox);
	gtk_box_pack_end(GTK_BOX(hbox),combobox,FALSE,FALSE,0);

	g_signal_connect(G_OBJECT(combobox),"changed",G_CALLBACK(powermanager_changed),key_cpufreq_ac_policy);

	gtk_combo_box_append_text(GTK_COMBO_BOX(combobox),_("On Demand"));
	gtk_combo_box_append_text(GTK_COMBO_BOX(combobox),_("Power Save"));
	gtk_combo_box_append_text(GTK_COMBO_BOX(combobox),_("Performance"));

	if(!g_ascii_strncasecmp(gconf_client_get_string(client,key_cpufreq_ac_policy,NULL),"ondemand",8)){
		gtk_combo_box_set_active(GTK_COMBO_BOX(combobox),0);
	}
	else if(!g_ascii_strncasecmp(gconf_client_get_string(client,key_cpufreq_ac_policy,NULL),"powersave",9)){
		gtk_combo_box_set_active(GTK_COMBO_BOX(combobox),1);
	}
	else if(!g_ascii_strncasecmp(gconf_client_get_string(client,key_cpufreq_ac_policy,NULL),"performance",9)){
		gtk_combo_box_set_active(GTK_COMBO_BOX(combobox),2);
	}

/*当使用电池时，CPU的使用策略*/
	hbox=gtk_hbox_new(FALSE,10);
	gtk_widget_show(hbox);
	gtk_box_pack_start(GTK_BOX(vbox),hbox,FALSE,FALSE,0);

	label=gtk_label_new(_("When using Battery power, CPU frequency policy is:"));
	gtk_widget_show(label);
	gtk_box_pack_start(GTK_BOX(hbox),label,FALSE,FALSE,0);

	combobox=gtk_combo_box_new_text();
	gtk_widget_show(combobox);
	gtk_box_pack_end(GTK_BOX(hbox),combobox,FALSE,FALSE,0);

	g_signal_connect(G_OBJECT(combobox),"changed",G_CALLBACK(powermanager_changed),key_cpufreq_battery_policy);

	gtk_combo_box_append_text(GTK_COMBO_BOX(combobox),_("On Demand"));
	gtk_combo_box_append_text(GTK_COMBO_BOX(combobox),_("Power Save"));
	gtk_combo_box_append_text(GTK_COMBO_BOX(combobox),_("Performance"));

	if(!g_ascii_strncasecmp(gconf_client_get_string(client,key_cpufreq_battery_policy,NULL),"ondemand",8)){
		gtk_combo_box_set_active(GTK_COMBO_BOX(combobox),0);
	}
	else if(!g_ascii_strncasecmp(gconf_client_get_string(client,key_cpufreq_battery_policy,NULL),"powersave",9)){
		gtk_combo_box_set_active(GTK_COMBO_BOX(combobox),1);
	}
	else if(!g_ascii_strncasecmp(gconf_client_get_string(client,key_cpufreq_battery_policy,NULL),"performance",9)){
		gtk_combo_box_set_active(GTK_COMBO_BOX(combobox),2);
	}
/*expander
	expander_powermanager=gtk_expander_new_with_mnemonic(_("Need some help? Click here!"));
	gtk_widget_show(expander_powermanager);
	g_signal_connect(G_OBJECT(expander_powermanager),"activate",G_CALLBACK(expander_change_powermanager),NULL);
	gtk_box_pack_end(GTK_BOX(main_vbox),expander_powermanager,FALSE,FALSE,0);

	expert_box_powermanager=gtk_vbox_new(FALSE,0);
	gtk_widget_set_size_request(GTK_WIDGET(expert_box_powermanager),200,100);
	gtk_widget_show(expert_box_powermanager);
	gtk_container_add(GTK_CONTAINER(expander_powermanager),expert_box_powermanager);*/

	return main_vbox; 
}
