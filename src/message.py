import abc


class Message(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def validate(self, signature_service):
        """Validates all of the necessary signatures.
        
        Args:
            signature_service (SignatureService): contains all keys for the
            client and servers
            
        Returns:
            bool
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def to_json(self):
        """Returns JSON version of this message (unicode)"""
        raise NotImplementedError()

    @staticmethod
    def from_json(self, json):
        """Returns the correct Message subclass from the json.

        Args:
            json (unicode): includes type field

        Returns:
            Message
        """
        pass


class GetMessage(Message):
    def __init__(self, key, client_id, signature_service):
        """Constructs message

        Args:
            key (string)
            client_id (int)
            signature_service (SignatureService)
        """
        pass

    @property
    def timestamp(self):
        pass

    @property
    def key(self):
        pass

    @property
    def client_id(self):
        pass

    def validate(self, signature_service):
        pass

    def to_json(self):
        pass


class DecryptionShareMessage(Message):
    def __init__(self, decryption_share, sender_id, get_message, signature_service):
        """Constructs

        Args:
            decryption_share (DecryptionShare)
            sender_id (int)
            get_message (GetMessage)
            signature_service (SignatureService)
        """
        pass

    @property
    def decryption_share(self):
        pass

    @property
    def client_id(self):
        pass

    @property
    def key(self):
        pass

    @property
    def timestamp(self):
        pass

    @property
    def sender_id(self):
        pass

    def validate(self, signature_service):
        pass

    def to_json(self):
        pass


# TODO: Better name
class ResponseMessage(Message):
    def __init__(self, secret, sender_id, signature_service):
        """Constructs

        Args:
            secret (Secret)
            sender_id (int)
            signature_service (SignatureService)
        """
        pass

    @property
    def secret(self):
        pass

    @property
    def sender_id(self):
        pass

    def validate(self, signature_service):
        pass

    def to_json(self):
        pass


class PutMessage(Message):
    def __init__(self, key, secret, client_id, signature_service):
        """Client broadcasts this to servers to store new secret.

        Args:
            key (string)
            secret (Secret)
            client_id (int)
            signature_service (SignatureService)
        """
        pass

    @property
    def secret(self):
        pass

    @property
    def timestamp(self):
        pass

    @property
    def key(self):
        pass

    @property
    def client_id(self):
        pass

    def validate(self, signature_service):
        pass

    def to_json(self):
        pass


class PutAcceptMessage(Message):
    def __init__(self, put_message, sender_id, signature_service):
        """Servers broadcast this to each other on accepting a PutMessage.
        
        Args:
            put_message (PutMessage)
            sender_id (int)
            signature_service (SignatureService)
        """
        pass

    @property
    def secret(self):
        pass

    @property
    def timestamp(self):
        pass

    @property
    def key(self):
        pass

    @property
    def client_id(self):
        pass

    @property
    def sender_id(self):
        pass

    def validate(self, signature_service):
        pass

    def to_json(self):
        pass


class CatchUpRequestMessage(Message):
    def __init__(self, timestamps,
        """
        Args:
            timestamps: ({client_id: timestamp})
