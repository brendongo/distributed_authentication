import asyncore


class Address(object):
    def __init__(self, uuid, port, hostname, server):
        """Wrapper around uuid, port, server

        Args:
            uuid (int)
            port (int)
            server (bool): False if client
        """
        self._id = uuid
        self._port = port
        self._server = server
        self._hostname = hostname

    @property
    def id(self):
        return self._id

    @property
    def port(self):
        return self._port

    @property
    def server(self):
        return self._server

    @property
    def hostname(self):
        return self._hostname


class MessagingService(asyncore.dispatcher):
    def __init__(self, addresses, server):
        """Binds to a port and listens for connections.

        Args:
            addresses (list[Address]): contains id, port, (server or client)
            server (Server): either a client or server
        """
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        print "Binding to port: {}".format(server.port)
        self.bind((server.host, server.port))
        self.listen(5)
        self._sockets = {}
        for addr in addresses:
            if addr.server and addr.port >= server.port:
                print "Trying to connect to: {}:{}".format(
                        addr.hostname, addr.port)
                socket = Socket((addr.hostname, addr.port))
                self._sockets[addr.id] = socket

    def send(self, message, destination_id):
        """Send message to destination

        Args:
            message (Message)
            destination_id (int)
        """
        pass

    def broadcast(self, message):
        """Send message to all servers

        Args:
            message (Message)
        """
        pass

    def handle_accept(self):
        """Opens a connection"""
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print 'Incoming connection from %s' % repr(pair)
            socket = Socket(sock=sock)
            socket.send("Accepted connection from: {}".format(pair))
            socket.send("We did it!")


class Socket(asyncore.dispatcher_with_send):
    """Two-way connection between server and client / server
    
    Args:
        addr (int): ip address
        sock (socket)
        server (Server): Server who owns the MessagingService
    """
    def __init__(self, addr=None, sock=None, server):
        if sock is not None:
            asyncore.dispatcher_with_send.__init__(self, sock)
        else:
            asyncore.dispatcher_with_send.__init__(self)
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect(addr)

    def handle_read(self):
        """Receives data"""
        data = self.recv(8192)
        print "Received: {}".format(data)
