import abc
import json
from datetime import datetime
from tpke import serialize, deserialize1

class Message(object):
    __metaclass__ = abc.ABCMeta

    def set_signature(self, signature_service=None, signature=None):
        #assert signature_service or signature
        if signature is not None:
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
    def from_json(cls, json_obj):
        """Returns the correct Message subclass from the json.

        Args:
            json_obj (dict): json object

        Returns:
            Message
        """
        if json_obj["type"] == "INTRO":
            return IntroMessage.from_json(json_obj)
        elif json_obj["type"] == "LOGIN":
            return LoginRequest.from_json(json_obj)
        elif json_obj["type"] == "ENROLL":
            return EnrollRequest.from_json(json_obj)
        elif json_obj["type"] == "LOGIN_RESPONSE":
            return LoginResponse.from_json(json_obj)
        elif json_obj["type"] == "ENROLL_RESPONSE":
            return EnrollResponse.from_json(json_obj)
        elif json_obj["type"] == "GET":
            return GetMessage.from_json(json_obj)
        elif json_obj["type"] == "DECRYPTION_SHARE":
            return DecryptionShareMessage.from_json(json_obj)
        elif json_obj["type"] == "RESPONSE":
            return GetResponseMessage.from_json(json_obj)
        elif json_obj["type"] == "PUT":
            return PutMessage.from_json(json_obj)
        elif json_obj["type"] == "PUT_ACCEPT":
            return PutAcceptMessage.from_json(json_obj)
        elif json_obj["type"] == "PUT_COMPLETE":
            return PutCompleteMessage.from_json(json_obj)
        elif json_obj["type"] == "CATCH_UP_REQUEST":
            return CatchUpRequestMessage.from_json(json_obj)
        elif json_obj["type"] == "CATCH_UP_RESPONSE":
            return CatchUpResponseMessage.from_json(json_obj)
        assert False, "Unidentifiable type %s" % json_obj["type"]


class LoginRequest(Message):
    def __init__(self, username, u, user_id, timestamp=None):
        self._username = username
        self._u = u
        self._timestamp = timestamp
        if timestamp is None:
            self._timestamp = datetime.now().isoformat()

        self._user_id = user_id

    def to_json(self):
        return json.dumps(
            {"type": "LOGIN",
             "username": self.username, "u": self.u.encode('base-64'),
             "timestamp": self.timestamp, "user_id": self.user_id})

    @property
    def u(self):
        return self._u

    @property
    def user_id(self):
        return self._user_id

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def username(self):
        return self._username

    @classmethod
    def from_json(cls, json_obj):
        assert json_obj["type"] == "LOGIN"
        return cls(
            json_obj["username"], json_obj["u"].decode('base-64'), json_obj["user_id"],
            timestamp=json_obj["timestamp"])

    def verify_signatures(self, signature_service=None):
        return True

    def __str__(self):
        return "LoginRequest ({})".format(self.username)
    __repr__ = __str__


class EnrollRequest(Message):
    def __init__(self, username, password, user_id, timestamp=None):
        self._username = username
        self._password = password
        self._timestamp = timestamp
        if timestamp is None:
            self._timestamp = datetime.now().isoformat()
        self._user_id = user_id

    def to_json(self):
        return json.dumps(
            {"type": "ENROLL",
             "username": self.username, "password": self.password,
             "timestamp": self.timestamp, "user_id": self.user_id})

    @property
    def password(self):
        return self._password

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def user_id(self):
        return self._user_id

    @property
    def username(self):
        return self._username

    @classmethod
    def from_json(cls, json_obj):
        assert json_obj["type"] == "ENROLL"
        return cls(
                json_obj["username"], json_obj["password"],
                json_obj["user_id"], json_obj["timestamp"])

    def verify_signatures(self, signature_service=None):
        return True

    def __str__(self):
        return "EnrollRequest ({})".format(self.username)
    __repr__ = __str__


class LoginResponse(Message):
    def __init__(self, username, v, encrypted, timestamp=None):
        self._username = username
        self._v = v
        self._encrypted = encrypted
        self._timestamp = timestamp
        if timestamp is None:
            self._timestamp = datetime.now().isoformat()

    def to_json(self):
        return json.dumps(
            {"type": "LOGIN_RESPONSE",
             "username": self.username, "v": self.v.encode('base-64'),
             "encrypted": self.encrypted,
             "timestamp": self.timestamp})

    @property
    def v(self):
        return self._v

    @property
    def encrypted(self):
        return self._encrypted


    @property
    def timestamp(self):
        return self._timestamp

    @property
    def username(self):
        return self._username

    @classmethod
    def from_json(cls, json_obj):
        assert json_obj["type"] == "LOGIN_RESPONSE"
        return cls(
                json_obj["username"], json_obj["v"].decode('base-64'),
                json_obj["encrypted"], json_obj["timestamp"])

    def verify_signatures(self, signature_service=None):
        return True

    def __str__(self):
        return "LoginResponse ({})".format(self.username)
    __repr__ = __str__


class EnrollResponse(Message):
    def __init__(self, username, timestamp=None):
        self._username = username
        self._timestamp = timestamp
        if timestamp is None:
            self._timestamp = datetime.now().isoformat()

    def to_json(self):
        return json.dumps(
            {"type": "ENROLL_RESPONSE",
             "username": self.username, "timestamp": self.timestamp})

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def username(self):
        return self._username

    @classmethod
    def from_json(cls, json_obj):
        assert json_obj["type"] == "ENROLL_RESPONSE"
        return cls(json_obj["username"], json_obj["timestamp"])

    def verify_signatures(self, signature_service=None):
        return True

    def __str__(self):
        return "EnrollResponse ({})".format(self.username)
    __repr__ = __str__


class IntroMessage(Message):
    def __init__(self, uuid):
        self._id = uuid

    def to_json(self):
        return json.dumps({"type": "INTRO", "id": self._id})

    @property
    def id(self):
        return self._id

    @classmethod
    def from_json(cls, json_obj):
        assert json_obj["type"] == "INTRO"
        return cls(json_obj["id"])

    def verify_signatures(self, signature_service):
        raise NotImplementedError("no")

    def __str__(self):
        return "IntroMessage"
    __repr__ = __str__


class GetMessage(Message):
    def __init__(self, key, client_id, signature_service=None,
                 signature=None, timestamp=None):
        """Constructs message

        Args:
            key (string)
            client_id (int)
            signature_service (SignatureService)
        """
        self._key = key
        self._client_id = client_id
        self.set_signature(signature_service, signature)
        self._timestamp = timestamp
        if timestamp is None:
            self._timestamp = datetime.now().isoformat()

    @property
    def timestamp(self):
        return self._timestamp

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
        return signature_service.validate(
                self.data, self._client_id, self._signature)

    def to_json(self):
        return json.dumps({
            "type": "GET",
            "key": self._key,
            "client_id": self._client_id,
            "signature": self._signature,
            "timestamp": self.timestamp})

    @classmethod
    def from_json(cls, json_obj):
        assert json_obj["type"] == "GET"
        return cls(
            json_obj["key"], json_obj["client_id"],
            signature=json_obj["signature"],
            timestamp=json_obj["timestamp"])

    def __str__(self):
        return "GetMessage ({})".format(self.key)
    __repr__ = __str__


class DecryptionShareMessage(Message):
    def __init__(self, decryption_share, sender_id, get_message,
                 signature_service=None, signature=None):
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
        return "".join([serialize(self._decryption_share[0]).encode('base-64'),
                        serialize(self._decryption_share[1]).encode('base-64'),
                        str(self._sender_id),
                        self._get_message.data, self._get_message._signature])

    def verify_signatures(self, signature_service):
        return (self._get_message.verify_signatures(signature_service) and
                signature_service.validate(self.data, self._sender_id, self._signature))

    def to_json(self):
        return json.dumps({
            "type": "DECRYPTION_SHARE",
            "decryption_share_1": serialize(self._decryption_share[0]).encode('base-64'),
            "decryption_share_2": serialize(self._decryption_share[1]).encode('base-64'),
            "sender_id": self._sender_id,
            "get_message": self._get_message.to_json(),
            "signature": self._signature})

    @classmethod
    def from_json(cls, json_obj):
        assert json_obj["type"] == "DECRYPTION_SHARE"
        decryption_share_1 = deserialize1(json_obj["decryption_share_1"].decode('base-64'))
        decryption_share_2 = deserialize1(json_obj["decryption_share_2"].decode('base-64'))
        decryption_share = (decryption_share_1, decryption_share_2)
        return cls(decryption_share, json_obj["sender_id"],
                   Message.from_json(json.loads(json_obj["get_message"])),
                   signature=json_obj["signature"])

    def __str__(self):
        return "DecryptionShareMessage ({})".format(self.key)
    __repr__ = __str__


class GetResponseMessage(Message):
    def __init__(self, get_msg, secret, sender_id,
                 signature_service=None, signature=None):
        """Constructs

        Args:
            get_msg (string): get_msg that was got
            secret (Secret)
            sender_id (int)
            signature_service (SignatureService)
        """
        self._get_msg = get_msg
        self._secret = secret
        self._sender_id = sender_id
        self.set_signature(signature_service, signature)

    @property
    def get_msg(self):
        return self._get_msg

    @property
    def secret(self):
        return self._secret

    @property
    def sender_id(self):
        return self._sender_id

    @property
    def signature(self):
        return self._signature

    @property
    def data(self):
        return "".join([self._secret.encode('base-64'), str(self._sender_id)])

    def verify_signatures(self, signature_service):
        return signature_service.validate(self.data, self._sender_id, self._signature)

    def to_json(self):
        return json.dumps({
            "type": "RESPONSE", "get_msg": self.get_msg.to_json(),
            "secret": self._secret.encode('base-64'), "sender_id": self.sender_id,
            "signature": self.signature})

    @classmethod
    def from_json(cls, json_obj):
        assert json_obj["type"] == "RESPONSE"
        return cls(
                Message.from_json(json.loads(json_obj["get_msg"])),
                json_obj["secret"].decode('base-64'), json_obj["sender_id"],
                signature=json_obj["signature"])

    def __str__(self):
        return "GetResponseMessage ({})".format(self.key)
    __repr__ = __str__

class PutMessage(Message):
    def __init__(self, key, secret, client_id,
                 signature_service=None, signature=None, timestamp=None):
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
        self._timestamp = timestamp
        if timestamp is None:
            self._timestamp = datetime.now().isoformat()

    @property
    def secret(self):
        return self._secret

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def key(self):
        return self._key

    @property
    def client_id(self):
        return self._client_id

    @property
    def data(self):
        return "".join([self._key, self._secret.encode('base-64'), str(self._client_id)])

    def verify_signatures(self, signature_service):
        return signature_service.validate(
                self.data, self._client_id, self._signature)

    def to_json(self):
        return json.dumps({
            "type": "PUT",
            "key": self._key,
            "secret": self._secret.encode('base-64'),
            "client_id": self._client_id,
            "signature": self._signature,
            "timestamp": self.timestamp})

    @classmethod
    def from_json(cls, json_obj):
        assert json_obj["type"] == "PUT"
        return cls(
            json_obj["key"], json_obj["secret"].decode('base-64'), json_obj["client_id"],
            signature=json_obj["signature"],
            timestamp=json_obj["timestamp"])

    def __str__(self):
        return "PutMessage ({})".format(self.key)
    __repr__ = __str__


class PutAcceptMessage(Message):
    def __init__(self, put_message, sender_id, signature_service=None,
                 signature=None):
        """Servers broadcast this to each other on accepting a PutMessage.

        Args:
            put_message (PutMessage)
            sender_id (int)
            signature_service (SignatureService)
        """
        self._put_message = put_message
        self._sender_id = sender_id
        self.set_signature(signature_service, signature)

    @property
    def secret(self):
        return self._put_message.secret

    @property
    def timestamp(self):
        return self._put_message.timestamp

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
    def put_msg(self):
        return self._put_message

    @property
    def data(self):
        return "".join(
            [self._put_message.data, self._put_message._signature,
             str(self._sender_id)])

    def verify_signatures(self, signature_service):
        return (self._put_message.verify_signatures(signature_service) and
            signature_service.validate(self.data, self._sender_id, self._signature))

    def to_json(self):
        return json.dumps({
            "type": "PUT_ACCEPT",
            "put_message": self._put_message.to_json(),
            "sender_id": self._sender_id,
            "signature": self._signature})

    @classmethod
    def from_json(cls, json_obj):
        assert json_obj["type"] == "PUT_ACCEPT"
        return cls(
            Message.from_json(json.loads(json_obj["put_message"])),
            json_obj["sender_id"], signature=json_obj["signature"])

    def __str__(self):
        return "PutAcceptMessage ({})".format(self.key)
    __repr__ = __str__


class PutCompleteMessage(Message):
    def __init__(self, put_msg, sender_id, signature_service=None,
                 signature=None):
        """Send this when you receive 2f + 1 PutAcceptMessages

        Args:
            sender_id (int)
            signature_service (SignatureService)
        """
        self._put_msg = put_msg
        self._sender_id = sender_id
        self.set_signature(signature_service, signature)

    @property
    def timestamp(self):
        return self.put_msg.timestamp

    @property
    def sender_id(self):
        return self._sender_id

    @property
    def put_msg(self):
        return self._put_msg

    @property
    def key(self):
        return self._put_msg.key

    @property
    def data(self):
        return str(self._sender_id)

    def verify_signatures(self, signature_service):
        signature_service.validate(
                self.data, self._sender_id, self._signature)

    def to_json(self):
        return json.dumps({
            "type": "PUT_COMPLETE",
            "put_msg": self.put_msg.to_json(),
            "sender_id": self._sender_id,
            "signature": self._signature})

    @classmethod
    def from_json(cls, json_obj):
        assert json_obj["type"] == "PUT_COMPLETE"
        return cls(
            Message.from_json(json.loads(json_obj["put_msg"])),
            json_obj["sender_id"], signature=json_obj["signature"])

    def __str__(self):
        return "PutCompleteMessage ({})".format(self.key)
    __repr__ = __str__


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
            "type": "CATCH_UP_REQUEST",
            "sender_id": self._sender_id,
            "signature": self._signature})

    @classmethod
    def from_json(cls, json_obj):
        assert json_obj["type"] == "CATCH_UP_REQUEST"
        return cls(
            None, json_obj["sender_id"], signature=json_obj["signature"])


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
    def from_json(cls, json_obj):
        pass
