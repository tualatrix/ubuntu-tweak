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

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <stdlib.h>
#include "daemon.h"

static UtDaemon *utdaemon = NULL;

void
signal_received (gint signal)
{
  switch (signal)
    {
    case SIGTERM:
    case SIGABRT:
      g_object_unref (utdaemon);
      exit (0);
      break;
    default:
      break;
    }
}

int
main (int argc, char *argv[])
{
  GMainLoop *main_loop;
  gboolean debug = FALSE;
  gboolean no_daemon = FALSE;
  GOptionContext *context;
  GOptionEntry entries[] =
    {
      { "debug",     'd', 0, G_OPTION_ARG_NONE, &debug,     "Debug mode",     NULL },
      { "no-daemon", 'n', 0, G_OPTION_ARG_NONE, &no_daemon, "No daemon mode", NULL },
      { NULL }
    };

  g_type_init ();

  /* parse options */
  context = g_option_context_new (NULL);
  g_option_context_add_main_entries (context, entries, NULL);
  g_option_context_parse (context, &argc, &argv, NULL);
  g_option_context_free (context);

  signal (SIGTERM, signal_received);
  utdaemon = ut_daemon_get ();

  if (G_UNLIKELY (debug))
    ut_daemon_set_debug (utdaemon, TRUE);

  main_loop = g_main_loop_new (NULL, FALSE);
  g_main_loop_run (main_loop);

  return 0;
}
