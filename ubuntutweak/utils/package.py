import logging

import aptdaemon.client
import aptdaemon.errors

from aptdaemon.enums import *
from aptdaemon.gtk3widgets import AptErrorDialog, AptProgressDialog

from gi.repository import Gtk

log = logging.getLogger('package')

class AptWorker(object):

    def __init__(self, parent, finish_handler):
        self.win = parent
        self.finish_handler = finish_handler
        self.ac = aptdaemon.client.AptClient()

    def _run_transaction(self, transaction):
        dia = AptProgressDialog(transaction, parent=self.win)
        transaction.connect('finished', self.finish_handler)
        dia.run(close_on_finished=True, show_error=True,
                reply_handler=lambda: True,
                error_handler=self._on_error)

    def _on_error(self, error):
        try:
            raise error
        except aptdaemon.errors.NotAuthorizedError:
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
