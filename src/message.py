import abc
import json


class Message(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def verify_signatures(self, signature_service):
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

    @classmethod
    def from_json(cls, json_str):
        """Returns the correct Message subclass from the json.

        Args:
            json_str (unicode): includes type field

        Returns:
            Message
        """
        print "JSON: {}".format(json_str)
        msg = json.loads(json_str)
        if msg["type"] == "INTRO":
            return IntroMessage.from_json(json_str)


class IntroMessage(Message):
    def __init__(self, uuid):
        self._id = uuid

    def to_json(self):
        return json.dumps({"type": "INTRO", "id": self._id})

    @property
    def id(self):
        return self._id

    @classmethod
    def from_json(cls, json_str):
        msg_dict = json.loads(json_str)
        assert msg_dict["type"] == "INTRO"
        return IntroMessage(msg_dict["id"])

    def verify_signatures(self, signature_service):
        raise NotImplementedError("no")


class GetMessage(Message):
    def __init__(self, key, client_id, signature_service):
        """Constructs message

        Args:
            key (string)
            client_id (int)
            signature_service (SignatureService)
        """
        self._key = key
        self._client_id = client_id
        # TODO sign, timestamp

    @property
    def timestamp(self):
        pass

    @property
    def key(self):
        return self._key

    @property
    def client_id(self):
        return self._client_id

    def verify_signatures(self, signature_service):
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
        self._decryption_share = decryption_share
        self._sender_id = sender_id
        self._get_message = get_message
        # TODO sign

    @property
    def decryption_share(self):
        return self._decryption_share

    @property
    def client_id(self):
        return self._get_message.client_id

    @property
    def key(self):
        return self._get_message.key

    @property
    def timestamp(self):
        return self._get_message.timestamp

    @property
    def sender_id(self):
        return self._sender_id

    def verify_signatures(self, signature_service):
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
        self._secret = secret
        self._sender_id = sender_id
        # TODO sign timestamp

    @property
    def secret(self):
        return self._secret

    @property
    def sender_id(self):
        return self._sender_id

    def verify_signatures(self, signature_service):
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
        self._key = key
        self._secret = secret
        self._client_id = client_id
        # TODO sign timestampe

    @property
    def secret(self):
        return self._secret

    @property
    def timestamp(self):
        pass

    @property
    def key(self):
        return self._key

    @property
    def client_id(self):
        return self._client_id

    def verify_signatures(self, signature_service):
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
        self._put_message = put_message
        self._sender_id = sender_id
        # TODO sign

    @property
    def secret(self):
        return self._put_message.secret

    @property
    def timestamp(self):
        pass

    @property
    def key(self):
        return self._put_message.key

    @property
    def client_id(self):
        return self._put_message.client_id

    @property
    def sender_id(self):
        return self._sender_id

    def verify_signatures(self, signature_service):
        pass

    def to_json(self):
        pass


class PutCompleteMessage(Message):
    def __init__(self, sender_id, signature_service):
        """Send this when you receive 2f + 1 PutAcceptMessages

        Args:
            sender_id (int)
            signature_service (SignatureService)
        """
        self._sender_id = sender_id
        # TODO sign, timestamp

    @property
    def sender_id(self):
        return self._sender_id

    def verify_signatures(self, signature_service):
        pass

    def to_json(self):
        pass


class CatchUpRequestMessage(Message):
    def __init__(self, timestamps, sender_id, signature_service):
        """Send this when you reboot and need to learn about new puts that you
        didn't receive.

        Args:
            timestamps ({client_id: timestamp}): the latest timestamps per
                client that you know already know about
            sender_id (int)
            signature_service (SignatureService)
        """
        pass

    @property
    def sender_id(self):
        pass

    @property
    def timestamps(self):
        pass

    def verify_signatures(self, signature_service):
        pass

    def to_json(self):
        pass


class CatchUpResponseMessage(Message):
    def __init__(self, entries, sender_id, signature_service):
        """Responds to CatchUpRequestMessages with entries.

        Args:
            entries (list[Entry]): has user, encrypted secret, client_id,
                timestamp
            sender_id (int)
            signature_service (SignatureService)
        """
        pass

    @property
    def sender_id(self):
        pass

    @property
    def entries(self):
        pass

    def verify_signatures(self, signature_service):
        pass

    def to_json(self):
        pass
