import logging

import aptdaemon.client
import aptdaemon.errors

from aptdaemon.enums import *
from aptdaemon.gtk3widgets import AptErrorDialog, AptProgressDialog, AptConfirmDialog

from gi.repository import Gtk

log = logging.getLogger('package')

class AptWorker(object):

    def __init__(self, parent, finish_handler, data=None):
        self.parent = parent
        self.data = data
        self.finish_handler = finish_handler
        self.ac = aptdaemon.client.AptClient()

    def _simulate_trans(self, trans):
        trans.simulate(reply_handler=lambda: self._confirm_deps(trans),
                       error_handler=self._on_error)

    def _confirm_deps(self, trans):
        if [pkgs for pkgs in trans.dependencies if pkgs]:
            dia = AptConfirmDialog(trans, parent=self.parent)
            res = dia.run()
            dia.hide()
            if res != Gtk.ResponseType.OK:
                return
        self._run_transaction(trans)

    def _run_transaction(self, transaction):
        dia = AptProgressDialog(transaction, parent=self.parent)
        transaction.connect('finished', self.finish_handler, self.data)
        dia.run(close_on_finished=True, show_error=True,
                      reply_handler=lambda: True,
                      error_handler=self._on_error)

    def _on_error(self, error):
        try:
            raise error
        except aptdaemon.errors.NotAuthorizedError:
            log.debug("aptdaemon.errors.NotAuthorizedError")
            # Silently ignore auth failures
            return
        except aptdaemon.errors.TransactionFailed, error:
            log.error(error)
        except Exception, error:
            error = aptdaemon.errors.TransactionFailed(ERROR_UNKNOWN,
                                                       str(error))
        dia = AptErrorDialog(error)
        dia.run()
        dia.hide()

    def update_cache(self, *args):
        return self.ac.update_cache(reply_handler=self._run_transaction,
                                    error_handler=self._on_error)

    def remove_packages(self, packages, *args):
        self.ac.remove_packages(packages,
                                reply_handler=self._simulate_trans,
                                error_handler=self._on_error)
