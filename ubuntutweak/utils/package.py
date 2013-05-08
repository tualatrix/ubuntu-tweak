import logging

import apt
import apt_pkg
import aptdaemon.client
import aptdaemon.errors

from aptdaemon.enums import *
from aptdaemon.gtk3widgets import AptErrorDialog, AptProgressDialog, AptConfirmDialog

from gi.repository import Gtk, Gdk

from defer import inline_callbacks, return_value

from ubuntutweak.gui.gtk import post_ui, unset_busy
from ubuntutweak.common.debug import log_func

log = logging.getLogger('package')


class NewAptProgressDialog(AptProgressDialog):
    def run(self, attach=False, close_on_finished=True, show_error=True,
            reply_handler=None, error_handler=None):
        """Run the transaction and show the progress in the dialog.

        Keyword arguments:
        attach -- do not start the transaction but instead only monitor
                  an already running one
        close_on_finished -- if the dialog should be closed when the
                  transaction is complete
        show_error -- show a dialog with the error message
        """
        try:
            self._run(attach, close_on_finished, show_error, error_handler)
        except Exception, error:
            if error_handler:
                error_handler(error)
            else:
                raise
        if reply_handler:
            reply_handler()

    @inline_callbacks
    def _run(self, attach, close_on_finished, show_error, error_handler):
        parent = self.get_transient_for()
        sig = self._transaction.connect("finished", self._on_finished,
                                        close_on_finished, show_error)
        self._signals.append(sig)
        if attach:
            yield self._transaction.attach()
        else:
            if self.debconf:
                yield self._transaction.set_debconf_frontend("gnome")
            try:
                deferred = self._transaction.run()
                yield deferred
            except Exception, error:
                error_handler(error)
                self._transaction.emit('finished', '')
                yield deferred
        self.show_all()

    def _on_finished(self, transaction, status, close, show_error):
        if close:
            self.hide()
            if status == EXIT_FAILED and show_error:
                Gdk.threads_enter()
                err_dia = AptErrorDialog(self._transaction.error, self)
                err_dia.run()
                err_dia.hide()
                Gdk.threads_leave()
        self.emit("finished")


class AptWorker(object):
    cache = None

    @log_func(log)
    def __init__(self, parent,
                 finish_handler=None, error_handler=None,data=None):
        '''
        finish_handler: must take three parameter
        '''
        self.parent = parent
        self.data = data
        self.finish_handler = finish_handler
        if error_handler:
            self._on_error = error_handler
        self.ac = aptdaemon.client.AptClient()

    @log_func(log)
    def _simulate_trans(self, trans):
        trans.simulate(reply_handler=lambda: self._confirm_deps(trans),
                       error_handler=self._on_error)

    @post_ui
    def _confirm_deps(self, trans):
        if [pkgs for pkgs in trans.dependencies if pkgs]:
            dia = AptConfirmDialog(trans, parent=self.parent)
            res = dia.run()
            dia.hide()
            if res != Gtk.ResponseType.OK:
                log.debug("Response is: %s" % res)
                if self.finish_handler:
                    log.debug("Finish_handler...")
                    self.finish_handler(trans, 0, self.data)
                return
        self._run_transaction(trans)

    @log_func(log)
    def _run_transaction(self, transaction):
        dia = NewAptProgressDialog(transaction, parent=self.parent)
        if self.finish_handler:
            log.debug("Connect to finish_handler...")
            transaction.connect('finished', self.finish_handler, self.data)

        dia.run(close_on_finished=True, show_error=True,
                reply_handler=lambda: True,
                error_handler=self._on_error)

    @post_ui
    def _on_error(self, error):
        try:
            raise error
        except aptdaemon.errors.NotAuthorizedError:
            log.debug("aptdaemon.errors.NotAuthorizedError")
            # Silently ignore auth failures
            return
        except aptdaemon.errors.TransactionFailed, error:
            log.error("TransactionFailed: %s" % error)
        except Exception, error:
            log.error("TransactionFailed with unknown error: %s" % error)
            error = aptdaemon.errors.TransactionFailed(ERROR_UNKNOWN,
                                                       str(error))
        dia = AptErrorDialog(error)
        dia.run()
        dia.hide()

    def update_cache(self, *args):
        return self.ac.update_cache(reply_handler=self._run_transaction,
                                    error_handler=self._on_error)

    @log_func(log)
    def install_packages(self, packages, *args):
        self.ac.install_packages(packages,
                                 reply_handler=self._simulate_trans,
                                 error_handler=self._on_error)

    @log_func(log)
    def remove_packages(self, packages, *args):
        self.ac.remove_packages(packages,
                                reply_handler=self._simulate_trans,
                                error_handler=self._on_error)

    @log_func(log)
    def downgrade_packages(self, packages, *args):
        self.ac.commit_packages([], [], [], [], [], packages,
                                reply_handler=self._simulate_trans,
                                error_handler=self._on_error)

    @classmethod
    def get_cache(self):
        try:
            self.update_apt_cache()
        except Exception, e:
            self.is_apt_broken = True
            self.apt_broken_message = e
            log.error("Error happened when get_cache(): %s" % str(e))
        finally:
            return self.cache

    @classmethod
    def update_apt_cache(self, init=False):
        '''if init is true, force to update, or it will update only once'''
        if init or not getattr(self, 'cache'):
            apt_pkg.init()
            self.cache = apt.Cache()
