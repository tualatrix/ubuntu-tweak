#ifndef __INTERFACE_H_
#define __INTERFACE_H_

#include <gtk/gtk.h>

#include "ubuntu-tweak.h"

#include "session_page.h"
#include "icon_page.h"
#include "compiz_page.h"
#include "gnome_page.h"
#include "nautilus_page.h"
#include "powermanager_page.h"
#include "system_page.h"
#include "security_page.h"
#include "fcitx_page.h"
#include "about.h"

#define	UT_LOGO		PACKAGE_PIXMAPS_DIR"/ubuntu-tweak.png"
#define UT_BANNER	PACKAGE_PIXMAPS_DIR"/banner.png"
#define UT_WELCOME	PACKAGE_PIXMAPS_DIR"/welcome.png"
#define UT_STARTUP	PACKAGE_PIXMAPS_DIR"/startup.png"
#define UT_DESKTOP	PACKAGE_PIXMAPS_DIR"/desktop.png"
#define UT_ICON		PACKAGE_PIXMAPS_DIR"/icon.png"
#define UT_COMPIZ	PACKAGE_PIXMAPS_DIR"/compiz-fusion.png"
#define UT_GNOME	PACKAGE_PIXMAPS_DIR"/gnome.png"
#define UT_NAUTILUS	PACKAGE_PIXMAPS_DIR"/nautilus.png"
#define UT_SYSTEM	PACKAGE_PIXMAPS_DIR"/system.png"
#define UT_POWER	PACKAGE_PIXMAPS_DIR"/power-manager.png"
#define UT_SECURITY	PACKAGE_PIXMAPS_DIR"/security.png"
#define UT_SECU_OPTIONS	PACKAGE_PIXMAPS_DIR"/security-options.png"
#define UT_APPLICATION	PACKAGE_PIXMAPS_DIR"/applications.png"
#define UT_SESSION	PACKAGE_PIXMAPS_DIR"/session-properties.png"

GtkWidget *create_main_window(void);

#endif
