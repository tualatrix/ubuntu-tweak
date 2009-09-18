class FetchClient(object):
    '''The fetch client, will be usable both with local and remote.
    The auto-fetch and auto-check feature will be used through the global preference.
    '''

    def __init__(self, model):
        '''model represent the model name, such as scripts, templates'''
        self.model = model

    def _fetch_data(self, model):
        pass

    def check_connection(self):
        pass

    def check_remote_data(self):
        pass

    def fetch_remote_data(self):
        pass

    def check_local_data(self):
        pass

    def fetch_local_data(self):
        pass
