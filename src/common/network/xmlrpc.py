from xmlrpclib import ServerProxy, Error

proxy = ServerProxy('http://127.0.0.1:8000/xmlrpc/')

if __name__ == '__main__':
    print proxy.user.authenticate('tualatrix','123456')
    print proxy.func.test('tualatrix','123456', 'Hello World')
