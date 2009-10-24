import dbus

POLICY_KIT_ACTION = 'com.ubuntu-tweak.daemon'

class PolicyKitService(dbus.service.Object):
    '''A D-BUS service that uses PolicyKit for authorization.'''

    def _check_permission(self, sender, action=POLICY_KIT_ACTION):
        '''
        Verifies if the specified action is permitted, and raises
        an AccessDeniedException if not.

        The caller should use ObtainAuthorization() to get permission.
        '''

        try:
            if sender:
                kit = dbus.SystemBus().get_object('org.freedesktop.PolicyKit1', '/org/freedesktop/PolicyKit1/Authority')
                kit = dbus.Interface(kit, 'org.freedesktop.PolicyKit1.Authority')

                # Note that we don't use CheckAuthorization with bus name
                # details because we have no ways to get the PID of the
                # front-end, so we're left with checking that its bus name
                # is authorised instead
                # See http://bugzilla.gnome.org/show_bug.cgi?id=540912
                (granted, _, details) = kit.CheckAuthorization(
                                ('system-bus-name', {'name': sender}),
                                action, {}, dbus.UInt32(1), '', timeout=600)
                logging.info('authorization of system bus name \'%s\': %r', sender, granted)

                if not granted:
                    raise AccessDeniedException('Session not authorized by PolicyKit')

        except AccessDeniedException:
            raise

        except dbus.DBusException, ex:
            raise AccessDeniedException(ex.message)
