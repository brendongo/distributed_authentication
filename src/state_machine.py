import abc


class StateMachine(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def handle_message(self, message):
        raise NotImplementedError()


class PutStateMachine(object):
    """State for put

    Args:
        client_msg (PutMessage)
        server (Server)
    """
    def __init__(self, client_msg, server):
        self._acceptances = []  # List[server_id]

    def handle_message(self, message):
        pass


class GetStateMachine(object):
    def __init__(self, client_msg, server):
        """State for get
        
        Args:
            client_msg (GetMessage): message that this is handling
            server (Server)
        """
        self._decryption_shares = []  # List of (decryption share, server id)

    def handle_message(self, message):
        pass


class CatchupStateMachine(object):
    def __init__(self, server):
        """State for catching up on messages that haven't been seen before
        
        Args:
            server (Server)
        """
        self._catching_up = False  # Can False when you hear from 2f + 1
        self._entries = []
        self._servers = []

    def catch_up(self):
        pass

    def handle_message(self, message):
        pass
