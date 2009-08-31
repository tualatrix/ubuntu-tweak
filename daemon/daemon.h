/* -*- Mode: C; c-file-style: "gnu"; tab-width: 8 -*- */
/* Copyright (C) 2006 Carlos Garnacho
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation; either version 2 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
 *
 * Authors: Carlos Garnacho Parro  <carlosg@gnome.org>
 */

#ifndef __DAEMON_H__
#define __DAEMON_H__

#include <glib-object.h>

G_BEGIN_DECLS

#define UT_TYPE_DAEMON         (ut_daemon_get_type ())
#define UT_DAEMON(o)           (G_TYPE_CHECK_INSTANCE_CAST ((o), UT_TYPE_DAEMON, UtDaemon))
#define UT_DAEMON_CLASS(c)     (G_TYPE_CHECK_CLASS_CAST ((c),    UT_TYPE_DAEMON, UtDaemonClass))
#define UT_IS_DAEMON(o)        (G_TYPE_CHECK_INSTANCE_TYPE ((o), UT_TYPE_DAEMON))
#define UT_IS_DAEMON_CLASS(c)  (G_TYPE_CHECK_CLASS_TYPE ((o),    UT_TYPE_DAEMON))
#define UT_DAEMON_GET_CLASS(o) (G_TYPE_INSTANCE_GET_CLASS ((o),  UT_TYPE_DAEMON, UtDaemonClass))

typedef struct UtDaemon      UtDaemon;
typedef struct UtDaemonClass UtDaemonClass;

struct UtDaemon
{
  GObject parent;

  /*<private>*/
  gpointer _priv;
};

struct UtDaemonClass
{
  GObjectClass parent_class;
};

GType          ut_daemon_get_type (void);

UtDaemon *ut_daemon_get      (void);

void           ut_daemon_set_debug (UtDaemon *daemon,
					 gboolean       debug);
gboolean       ut_daemon_get_debug (UtDaemon *daemon);


G_END_DECLS

#endif /* __UT_DAEMON_H */
