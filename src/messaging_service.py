class MessagingService(object):
    def __init__(self, servers_filename, clientsfile=None):
        """Validates all of the necessary signatures.

        Args:
            servers_filename (string): filename of file that contains
            server_ids and portnumbers of all servers

            clients_filename (string): filename of file that contains
            client_ids and port numbers of all clients
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