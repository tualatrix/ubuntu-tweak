#include <gtk/gtk.h>

void show_about(gpointer data)
{
	gchar*  authors[] = {"TualatriX <tualatrix@gmail.com>", NULL};

	gchar*  license = 
	"作者还未决定使用以什么协议发布";

	gtk_show_about_dialog (NULL, 
	"authors", authors,
	"copyright", "Copyright © 2007 TualatriX",
	"translator-credits", "translator-credits",
	"license", license,
	"comments", "最优秀的Ubuntu系统下的设置优化工具"
	"version", "0.01",
	NULL);
}
