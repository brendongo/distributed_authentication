from threshold_encryption_service import ThresholdEncryptionService

class StubServer(object):
    def __init__(self, uid):
        self._id = uid
        self._threshold = ThresholdEncryptionService('thenc8_2.keys', uid)

    @property
    def id(self):
        return self._id

    @property
    def port(self):
        return 2

    @property
    def host(self):
        return 3

    @property
    def messaging_service(self):
        return StubMessagingService()

    @property
    def threshold_encryption_service(self):
        return self._threshold

    @property
    def signature_service(self):
        return StubSignatureService()

    @property
    def write_ahead_log(self):
        pass

    @property
    def secrets_db(self):
        from secrets_db import SecretsDB
        return SecretsDB('testdb')

    @property
    def catchup_state_machine(self):
        pass

    @property
    def f(self):
        return 2

    @property
    def N(self):
        return 7


class StubSignatureService(object):
    def sign(self, msg):
        return ""

    def validate(self, msg, sender, signature):
        return True


class StubThresholdEncryptionService():
    def encrypt(self, msg):
        """Takes a message and returns something."""
        return msg

    def decrypt(self, decryption_shares):
        """Takes decryption_shares and turns it into a message.

        Args:
            TODO

        Returns:
            TODO
        """
        print "Threshold Decrypted ", decryption_shares
        return decryption_shares[0]


class StubSecretsDb():
    def __init__(self):
        self.store = {}


    def get(self, key):
        print "DB Get ", key
        return self.store[key]

    def put(self, key, val):
        print "DB Put ", key, ":", val
        self.store[key] = val


class StubMessagingService():
    def __init__(self):
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
        print "Send message", message.__dict__, destination_id

    def broadcast(self, message):
        """Send message to all servers

        Args:
            message (Message)
        """
        print "Broadcast"
        print message

    def handle_accept(self):
        """Opens a connection"""
        pass
