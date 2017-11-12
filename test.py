import argparse
import asyncore
import socket

PORTS = [8080, 8081, 8082, 8083]

class Client(asyncore.dispatcher_with_send):
    def __init__(self, addr=None, sock=None):
        if sock is not None:
            asyncore.dispatcher_with_send.__init__(self, sock)
        else:
            asyncore.dispatcher_with_send.__init__(self)
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect(addr)

    def handle_read(self):
        data = self.recv(8192)
        print "Received: {}".format(data)

    def handle_connect(self):
        self.send("hello, world!")


class Server(asyncore.dispatcher):
    def __init__(self, host, index):
        asyncore.dispatcher.__init__(self)
        port = PORTS[index]
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        print "Binding to port: {}".format(port)
        self.bind(('0.0.0.0', port))
        self.listen(5)
        for i in xrange(index):
            print "Trying to connect to: {}".format(PORTS[i])
            client = Client(('localhost', PORTS[i]))

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print 'Incoming connection from %s' % repr(pair)
            handler = Client(sock=sock)
            handler.send("Accepted connection from: {}".format(pair))
            handler.send("We did it!")

parser = argparse.ArgumentParser()
parser.add_argument("port_index", type=int)
args = parser.parse_args()
server = Server('localhost', args.port_index)
asyncore.loop()
