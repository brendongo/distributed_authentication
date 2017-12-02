import asyncore


class Address(object):
    def __init__(self, uuid, port, server):
        """Wrapper around uuid, port, server

        Args:
            uuid (int)
            port (int)
            server (bool): False if client
        """
        self._id = uuid
        self._port = port
        self._server = server

    @property
    def id(self):
        return self._id

    @property
    def port(self):
        return self._port

    @property
    def server(self):
        return self._server


class MessagingService(asyncore.dispatcher):
    def __init__(self, addresses, server):
        """Binds to a port and listens for connections.

        Args:
            addresses (list[Address]): contains id, port, (server or client)
            server (Server): either a client or server
        """
        pass

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
        pass


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
        pass
