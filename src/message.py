import abc
import json
from tpke import serialize

class Message(object):
    __metaclass__ = abc.ABCMeta

    def set_signature(self, signature_service=None, signature=None):
        assert signature_service or signature
        if signature:
            self._signature = signature
        else:
            self._signature = signature_service.sign(self.data)

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

    @property
    def data(self):
        """Returns raw data of this message (not including the signature)"""
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
        elif msg["type"] == "GET":
            return GetMessage.from_json(json_str)
        elif msg["type"] == "DECRYPTION_SHARE":
            return DecryptionShareMessage.from_json(json_str)
        elif msg["type"] == "RESPONSE":
            return ResponseMessage.from_json(json_str)
        elif msg["type"] == "PUT":
            return PutMessage.from_json(json_str)
        elif msg["type"] == "PUT_ACCEPT":
            return PutAcceptMessage.from_json(json_str)
        elif msg["type"] == "PUT_COMPLETE":
            return PutCompleteMessage.from_json(json_str)
        elif msg["type"] == "CATCH_UP_REQUEST":
            return CatchUpRequestMessage.from_json(json_str)
        elif msg["type"] == "CATCH_UP_RESPONSE":
            return CatchUpResponseMessage.from_json(json_str)
        assert False, "Unidentifiable type %s" % msg["type"]

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
    def __init__(self, key, client_id, signature_service=None, signature=None):
        """Constructs message

        Args:
            key (string)
            client_id (int)
            signature_service (SignatureService)
        """
        self._key = key
        self._client_id = client_id
        self.set_signature(signature_service, signature)

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

    @property
    def data(self):
        return "".join([self._key, str(self._client_id)])

    def verify_signatures(self, signature_service):
        return signature_service.validate(self.data, self._client_id, self._signature)

    def to_json(self):
        return json.dumps({
            type: "GET", 
            key: self._key, 
            client_id: self._client_id, 
            signature: self._signature})

    @classmethod
    def from_json(cls, json_str):
        msg_dict = json.loads(json_str)
        assert msg_dict["type"] == "GET"
        return GetMessage(msg_dict["key"], msg_dict["client_id"], signature=msg_dict["signature"])
        pass

class DecryptionShareMessage(Message):
    def __init__(self, decryption_share, sender_id, get_message, signature_service=None, signature=None):
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
        self.set_signature(signature_service, signature)
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

    @property
    def data(self):
        return "".join([serialize(self._decryption_share),
                        str(self._sender_id), 
                        self._get_message.data, self._get_message._signature])

    def verify_signatures(self, signature_service):
        return (self._get_message.verify_signatures(signature_service) and
                signature_service.validate(self.data, self._sender_id, self._signature))

    def to_json(self):
        return json.dumps({
            type: "DECRYPTION_SHARE",
            decryption_share: self._decryption_share,
            sender_id: self._sender_id,
            get_message: self._get_message.to_json(),
            signature: self._signature})

    @classmethod
    def from_json(cls, json_str):
        msg_dict = json.loads(json_str)
        assert msg_dict["type"] == "DECRYPTION_SHARE"
        return DecryptionShareMessage(msg_dict["decryption_share"], msg_dict["sender_id"], 
                    msg_dict["get_message"], signature=msg_dict["signature"])

# TODO: Better name
class ResponseMessage(Message):
    def __init__(self, secret, sender_id, signature_service=None, signature=None):
        """Constructs

        Args:
            secret (Secret)
            sender_id (int)
            signature_service (SignatureService)
        """
        self._secret = secret
        self._sender_id = sender_id
        self.set_signature(signature_service, signature)
        # TODO sign timestamp

    @property
    def secret(self):
        return self._secret

    @property
    def sender_id(self):
        return self._sender_id

    @property
    def data(self):
        return "".join([self._secret, str(self._sender_id)])

    def verify_signatures(self, signature_service):
        return signature_service.validate(self.data, self._sender_id, self._signature)

    def to_json(self):
        return json.dumps({
            type: "RESPONSE",
            secret: self._secret,
            sender_id: self._sender_id,
            signature: self._signature})

    @classmethod
    def from_json(cls, json_str):
        msg_dict = json.loads(json_str)
        assert msg_dict["type"] == "RESPONSE"
        return ResponseMessage(msg_dict["secret"], msg_dict["sender_id"], signature=msg_dict["signature"])

class PutMessage(Message):
    def __init__(self, key, secret, client_id, signature_service=None, signature=None):
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
        self.set_signature(signature_service, signature)
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

    @property 
    def data(self):
        return "".join([self._key, self._secret, str(self._client_id)])

    def verify_signatures(self, signature_service):
        return signature_service.validate(self.data, self._client_id, self._signature)

    def to_json(self):
        return json.dumps({
            type: "PUT",
            key: self._key,
            secret: self._secret,
            client_id: self._client_id,
            signature: self._signature})

    @classmethod
    def from_json(cls, json_str):
        msg_dict = json.loads(json_str)
        assert msg_dict["type"] == PUT
        return PutMessage(msg_dict["key"], msg_dict["secret"], msg_dict["client_id"], signature=msg_dict["signature"])

class PutAcceptMessage(Message):
    def __init__(self, put_message, sender_id, signature_service=None, signature=None):
        """Servers broadcast this to each other on accepting a PutMessage.

        Args:
            put_message (PutMessage)
            sender_id (int)
            signature_service (SignatureService)
        """
        self._put_message = put_message
        self._sender_id = sender_id
        self.set_signature(signature_service, signature)
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

    @property
    def data(self):
        return "".join([self._put_message.data, self._put_message._signature, str(self._sender_id)])

    def verify_signatures(self, signature_service):
        return (self._put_message.verify_signatures(signature_service) and
            signature_service.validate(self.data, self._sender_id, self._signature))

    def to_json(self):
        return json.dumps({
            type: "PUT_ACCEPT",
            put_message: self._put_message.to_json(),
            sender_id: self._sender_id,
            signature: self._signature})

    @classmethod
    def from_json(cls, json_str):
        msg_dict = json.loads(json_str)
        assert msg_dict["type"] == "PUT_ACCEPT"
        return PutAcceptMessages(msg_dict["put_message"], msg_dict["sender_id"], signature=msg_dict["signature"])

class PutCompleteMessage(Message):
    def __init__(self, sender_id, signature_service=None, signature=None):
        """Send this when you receive 2f + 1 PutAcceptMessages

        Args:
            sender_id (int)
            signature_service (SignatureService)
        """
        self._sender_id = sender_id
        self.set_signature(signature_service, signature)
        # TODO sign, timestamp

    @property
    def sender_id(self):
        return self._sender_id

    @property
    def data(self):
        return str(self._sender_id)

    def verify_signatures(self, signature_service):
        signature_service.validate(self.data, self._sender_id, self._signature)

    def to_json(self):
        return json.dumps({
            type: "PUT_COMPLETE",
            sender_id: self._sender_id,
            signature: self._signature})

    @classmethod
    def from_json(cls, json_str):
        msg_dict = json.loads(json_str)
        assert msg_dict["type"] == "PUT_COMPLETE"
        return PutCompleteMessage(msg_dict["sender_id"], signature=msg_dict["signature"])

class CatchUpRequestMessage(Message):
    def __init__(self, timestamps, sender_id, signature_service=None, signature=None):
        """Send this when you reboot and need to learn about new puts that you
        didn't receive.

        Args:
            timestamps ({client_id: timestamp}): the latest timestamps per
                client that you know already know about
            sender_id (int)
            signature_service (SignatureService)
        """

        # TODO: WHAT TO DO WITH TIMESTAMPS??
        self._sender_id = sender_id
        self.set_signature(signature_service, signature)

    @property
    def sender_id(self):
        return self._sender_id

    @property
    def timestamps(self):
        return self._timestamps

    @property
    def data(self):
        return "".join([])
        return str(self.sender_id)

    def verify_signatures(self, signature_service):
        return signature_service.validate(self.data, self._sender_id, self._signature)

    def to_json(self):
        return json.dumps({
            type: "CATCH_UP_REQUEST",
            sender_id: self._sender_id,
            signature: self._signature})

    @classmethod
    def from_json(cls, json_str):
        msg_dict = json.loads(json_str)
        assert msg_dict["type"] == "CATCH_UP_REQUEST"
        return CatchUpRequestMessage(None, msg_dict["sender_id"], signature=msg_dict["signature"])

class CatchUpResponseMessage(Message):
    def __init__(self, entries, sender_id, signature_service):
        """Responds to CatchUpRequestMessages with entries.

        Args:
            entries (list[Entry]): has user, encrypted secret, client_id,
                timestamp
            sender_id (int)
            signature_service (SignatureService)
        """
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

    @classmethod
    def from_json(cls, json_str):
        pass
