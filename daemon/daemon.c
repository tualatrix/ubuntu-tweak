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

#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>

#include <glib.h>
#include <glib-object.h>
#include <dbus/dbus.h>
#include <dbus/dbus-glib-lowlevel.h>
#include "daemon.h"

#include <polkit/polkit.h>
#include <polkit-dbus/polkit-dbus.h>

#define DBUS_ADDRESS_ENVVAR "DBUS_SESSION_BUS_ADDRESS"
#define DBUS_INTERFACE_UT "com.ubuntu_tweak.daemon"
#define UT_ACTION_ID "com.ubuntu-tweak.daemon"

#define UT_DAEMON_GET_PRIVATE(o) (G_TYPE_INSTANCE_GET_PRIVATE ((o), UT_TYPE_DAEMON, UtDaemonPrivate))

#define DEBUG(d,m...) \
if (G_UNLIKELY (((UtDaemonPrivate *) d->_priv)->debug)) \
  { \
    g_debug (m); \
  }

enum {
  PROP_0,
  PROP_DEBUG
};

typedef struct UtDaemonPrivate   UtDaemonPrivate;
typedef struct UtDaemonAsyncData UtDaemonAsyncData;

struct UtDaemonPrivate
{
  DBusConnection *connection;
  gchar *platform;

  PolKitContext *polkit_context;

  guint debug : 1;
};

struct UtDaemonAsyncData
{
  UtDaemon *daemon;
  gchar *destination;
  gint serial;
};

static void     ut_daemon_class_init  (UtDaemonClass    *class);
static void     ut_daemon_init        (UtDaemon         *object);
static void     ut_daemon_finalize    (GObject               *object);

static GObject* ut_daemon_constructor (GType                  type,
					    guint                  n_construct_properties,
					    GObjectConstructParam *construct_params);

static void     ut_daemon_set_property (GObject      *object,
					     guint         prop_id,
					     const GValue *value,
					     GParamSpec   *pspec);
static void     ut_daemon_get_property (GObject      *object,
					     guint         prop_id,
					     GValue       *value,
					     GParamSpec   *pspec);

static gchar*   get_destination            (DBusMessage *message);


G_DEFINE_TYPE (UtDaemon, ut_daemon, G_TYPE_OBJECT);

static void
ut_daemon_class_init (UtDaemonClass *class)
{
  GObjectClass *object_class = G_OBJECT_CLASS (class);

  object_class->constructor = ut_daemon_constructor;
  object_class->set_property = ut_daemon_set_property;
  object_class->get_property = ut_daemon_get_property;
  object_class->finalize = ut_daemon_finalize;

  g_object_class_install_property (object_class,
				   PROP_DEBUG,
				   g_param_spec_boolean ("debug", "", "",
							 FALSE,
							 G_PARAM_READWRITE));
  g_type_class_add_private (object_class,
			    sizeof (UtDaemonPrivate));
}

static void
async_data_free (UtDaemonAsyncData *data)
{
  g_object_unref (data->daemon);
  g_free (data->destination);
  g_free (data);
}

static gchar *
retrieve_platform (DBusMessage *message)
{
      DBusMessageIter iter;
      const gchar *str;

      dbus_message_iter_init (message, &iter);
      dbus_message_iter_get_basic (&iter, &str);

      if (str && *str)
	return g_strdup (str);

      return NULL;
}

static void
dispatch_reply (DBusPendingCall *pending_call,
		gpointer         data)
{
  UtDaemonPrivate *priv;
  DBusMessage *reply;
  UtDaemonAsyncData *async_data;
  DBusError error;

  reply = dbus_pending_call_steal_reply (pending_call);
  async_data = (UtDaemonAsyncData *) data;
  priv = async_data->daemon->_priv;
  dbus_error_init (&error);

  DEBUG (async_data->daemon, "sending reply from: %s", dbus_message_get_path (reply));

  if (dbus_set_error_from_message (&error, reply))
    {
      g_warning (error.message);
      dbus_error_free (&error);
    }

  /* send the reply back */
  dbus_message_set_destination (reply, async_data->destination);
  dbus_message_set_reply_serial (reply, async_data->serial);
  dbus_connection_send (priv->connection, reply, NULL);

  dbus_message_unref (reply);
}

static gchar*
get_destination (DBusMessage *message)
{
  gchar **arr, *destination = NULL;

  if (!dbus_message_get_path_decomposed (message, &arr))
    return NULL;

  if (!arr)
    return NULL;

  /* paranoid check */
  if (arr[0] && strcmp (arr[0], "com") == 0 &&
      arr[1] && strcmp (arr[1], "ubuntu_tweak") == 0 &&
      arr[2] && strcmp (arr[2], "daemon") == 0 && arr[3] && !arr[4])
    destination = g_strdup_printf (DBUS_INTERFACE_UT ".%s", arr[3]);

  dbus_free_string_array (arr);

  return destination;
}

static gboolean
can_caller_do_action (UtDaemon *daemon,
		      DBusMessage   *message,
		      const gchar   *name)
{
  UtDaemonPrivate *priv;
  PolKitAction *action;
  PolKitCaller *caller;
  DBusError error;
  PolKitResult result;
  const gchar *member;
  gboolean retval;
  gchar *destination;

  priv = UT_DAEMON_GET_PRIVATE (daemon);
  member = dbus_message_get_member (message);

  g_return_val_if_fail (member != NULL, FALSE);

  action = polkit_action_new ();

  destination = get_destination(message);

  polkit_action_set_action_id (action, UT_ACTION_ID);

  g_debug("the polkit action_id is %s", UT_ACTION_ID);

  dbus_error_init (&error);
  caller = polkit_caller_new_from_dbus_name (priv->connection, dbus_message_get_sender (message), &error);

  if (dbus_error_is_set (&error))
    {
      g_critical (error.message);
      dbus_error_free (&error);

      return FALSE;
    }

  result = polkit_context_is_caller_authorized(priv->polkit_context, action, caller, TRUE, NULL);

  polkit_caller_unref (caller);
  polkit_action_unref (action);

  retval = (result == POLKIT_RESULT_YES);

  DEBUG (daemon,
	 (retval) ? "caller is allowed to do action '%s'" : "caller can't do action '%s'",
	 UT_ACTION_ID);

  g_free (destination);

  return retval;
}

static void
dispatch_ut_message (UtDaemon *daemon,
		      DBusMessage   *message,
		      gint           serial)
{
  UtDaemonPrivate *priv;
  DBusMessage *copy;
  DBusPendingCall *pending_call;
  UtDaemonAsyncData *async_data;
  gchar *destination;
  gchar *interface;

  priv = UT_DAEMON_GET_PRIVATE (daemon);
  destination = get_destination (message);

  /* there's something wrong with the message */
  DEBUG (daemon, "the message's destination is to: %s", destination);
  if (G_UNLIKELY (!destination))
    {
      g_critical ("Could not get a valid destination, original one was: %s", dbus_message_get_path (message));
      return;
    }

  DEBUG (daemon, "dispatching message to: %s", dbus_message_get_path (message));

  interface = dbus_message_get_interface (message);
  DEBUG (daemon, "the message has interface: %s", interface);

  if (strcmp(interface, DBUS_INTERFACE_INTROSPECTABLE) != 0){
	  dbus_message_set_interface(message, destination);
  }

  copy = dbus_message_copy (message);

  /* forward the message to the corresponding service */
  dbus_message_set_destination (copy, destination);
  dbus_connection_send_with_reply (priv->connection, copy, &pending_call, -1);

  if (pending_call)
    {
      async_data = g_new0 (UtDaemonAsyncData, 1);
      async_data->daemon = g_object_ref (daemon);
      async_data->destination = g_strdup (dbus_message_get_sender (message));
      async_data->serial = (serial) ? serial : dbus_message_get_serial (message);

      dbus_pending_call_set_notify (pending_call, dispatch_reply, async_data, (DBusFreeFunction) async_data_free);
      dbus_pending_call_unref (pending_call);
    }

  g_free (destination);
  dbus_message_unref (copy);
}

static void
return_error (UtDaemon *daemon,
	      DBusMessage   *message,
	      const gchar   *error_name)
{
  DBusMessage *reply;
  UtDaemonPrivate *priv;

  priv = UT_DAEMON_GET_PRIVATE (daemon);

  DEBUG (daemon, "sending error %s from: %s", error_name, dbus_message_get_path (message));

  reply = dbus_message_new_error (message, error_name,
				  "No permissions to perform the task.");
  dbus_connection_send (priv->connection, reply, NULL);
  dbus_message_unref (reply);
}

static DBusHandlerResult
daemon_filter_func (DBusConnection *connection,
			DBusMessage    *message,
			void           *data)
{
  UtDaemon *daemon = UT_DAEMON (data);

  if (dbus_message_is_signal (message, DBUS_INTERFACE_LOCAL, "Disconnected"))
    {
      /* FIXME: handle Disconnect */
    }
  else if (dbus_message_is_signal (message, DBUS_INTERFACE_DBUS, "NameOwnerChanged"))
    {
      /* FIXME: handle NameOwnerChanged */
    }
  else if (dbus_message_has_interface (message, DBUS_INTERFACE_INTROSPECTABLE))
    dispatch_ut_message (daemon, message, 0);
  else if (dbus_message_has_interface (message, DBUS_INTERFACE_UT))
    {
      if (can_caller_do_action (daemon, message, NULL))
	dispatch_ut_message (daemon, message, 0);
      else
	return_error (daemon, message, DBUS_ERROR_ACCESS_DENIED);
    }

  return DBUS_HANDLER_RESULT_HANDLED;
}

static void
setup_connection (UtDaemon *daemon)
{
  UtDaemonPrivate *priv;
  DBusError error;

  priv = UT_DAEMON_GET_PRIVATE (daemon);
  dbus_error_init (&error);

  priv->connection = dbus_bus_get (DBUS_BUS_SYSTEM, &error);

  if (dbus_error_is_set (&error))
    {
      g_critical (error.message);
      dbus_error_free (&error);
    }

  dbus_connection_set_exit_on_disconnect (priv->connection, FALSE);
  dbus_connection_add_filter (priv->connection, daemon_filter_func, daemon, NULL);
  dbus_bus_request_name (priv->connection, DBUS_INTERFACE_UT, 0, &error);

  if (dbus_error_is_set (&error))
    {
      g_critical (error.message);
      dbus_error_free (&error);
    }

  dbus_connection_setup_with_g_main (priv->connection, NULL);
}

static gboolean
ut_polkit_io_watch_func (GIOChannel   *channel,
			  GIOCondition  condition,
			  gpointer      user_data)
{
  int fd;
  PolKitContext *pk_context;

  pk_context = (PolKitContext *) user_data;
  fd = g_io_channel_unix_get_fd (channel);
  polkit_context_io_func (pk_context, fd);

  return TRUE;
}

static int
ut_polkit_io_add_watch (PolKitContext *context,
			 int            fd)
{
  guint watch_id = 0;
  GIOChannel *channel;

  channel = g_io_channel_unix_new (fd);

  if (!channel)
    return 0;

  watch_id = g_io_add_watch (channel, G_IO_IN, ut_polkit_io_watch_func, context);
  g_io_channel_unref (channel);

  return watch_id;
}

static void
ut_polkit_io_remove_watch (PolKitContext *context,
			    int            watch_id)
{
  g_source_remove (watch_id);
}

static void
ut_daemon_init (UtDaemon *daemon)
{
  UtDaemonPrivate *priv;

  priv = UT_DAEMON_GET_PRIVATE (daemon);
  daemon->_priv = priv;

  setup_connection (daemon);

  /* we're screwed if we don't have this */
  g_assert (priv->connection != NULL);

  priv->polkit_context = polkit_context_new ();
  polkit_context_set_io_watch_functions (priv->polkit_context,
					 ut_polkit_io_add_watch,
					 ut_polkit_io_remove_watch);

  polkit_context_init (priv->polkit_context, NULL);
}

static void
ut_daemon_set_property (GObject      *object,
			     guint         prop_id,
			     const GValue *value,
			     GParamSpec   *pspec)
{
  switch (prop_id)
    {
    case PROP_DEBUG:
      ut_daemon_set_debug (UT_DAEMON (object),
				g_value_get_boolean (value));
      break;
    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
    }
}

static void
ut_daemon_get_property (GObject      *object,
			     guint         prop_id,
			     GValue       *value,
			     GParamSpec   *pspec)
{
  switch (prop_id)
    {
    case PROP_DEBUG:
      g_value_set_boolean (value,
			   ut_daemon_get_debug (UT_DAEMON (object)));
      break;
    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
    }
}

static void
ut_daemon_finalize (GObject *object)
{
  UtDaemonPrivate *priv;

  priv = UT_DAEMON_GET_PRIVATE (object);

  dbus_connection_unref (priv->connection);

  polkit_context_unref  (priv->polkit_context);

  g_free (priv->platform);

  G_OBJECT_CLASS (ut_daemon_parent_class)->finalize (object);
}

static GObject*
ut_daemon_constructor (GType                  type,
			    guint                  n_construct_properties,
			    GObjectConstructParam *construct_params)
{
  static GObject *object = NULL;

  if (!object)
    object = G_OBJECT_CLASS (ut_daemon_parent_class)->constructor (type,
									n_construct_properties,
									construct_params);
  return object;
}

UtDaemon*
ut_daemon_get (void)
{
  return g_object_new (UT_TYPE_DAEMON, NULL);
}

void
ut_daemon_set_debug (UtDaemon *daemon,
			  gboolean       debug)
{
  UtDaemonPrivate *priv;

  g_return_if_fail (UT_IS_DAEMON (daemon));

  priv = UT_DAEMON_GET_PRIVATE (daemon);
  priv->debug = debug;
  g_object_notify (G_OBJECT (daemon), "debug");
}

gboolean
ut_daemon_get_debug (UtDaemon *daemon)
{
  UtDaemonPrivate *priv;

  g_return_val_if_fail (UT_IS_DAEMON (daemon), FALSE);

  priv = UT_DAEMON_GET_PRIVATE (daemon);
  return priv->debug;
}
