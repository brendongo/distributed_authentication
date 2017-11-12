import argparse
import asyncore
import socket

PORTS = [8080, 8081, 8082, 8083]

class Client(asyncore.dispatcher_with_send):
    def handle_read(self):
        data = self.recv(8192)
        print "Received: {}".format(data)


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
            self.connect(('localhost', PORTS[i]))

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print 'Incoming connection from %s' % repr(pair)
            handler = Client(sock)
            handler.send("Accepted connection from: {}".format(pair))


class Client(asyncore.dispatcher_with_send):
    def __init__(self):
        asyncore.dispatcher_with_send.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(('0.0.0.0', 8081))
        self.listen(5)
        self.connect(("127.0.0.1", 8080))

    def handle_connect(self):
        self.send("Hello, world!")

parser = argparse.ArgumentParser()
parser.add_argument("port_index", type=int)
args = parser.parse_args()
if args.port_index == 0:
    server = Server('localhost', args.port_index)
else:
    client = Client()
#server = Server('localhost', args.port_index)
asyncore.loop()
