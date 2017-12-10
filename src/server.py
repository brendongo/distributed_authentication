import asyncore
from signature_service import SignatureService
from threshold_encryption_service import ThresholdEncryptionService
from secrets_db import SecretsDB

from message import GetMessage
from message import DecryptionShareMessage
from message import PutMessage
from message import PutAcceptMessage
from state_machine import GetStateMachine
from state_machine import PutStateMachine
from utils import CONSTANTS

class Server(object):
    def __init__(self, uid):
        """
        Args:
            config_filename (string): contains threshold encryption keys,
                signature private key, signature public keys, location info
                about servers, server id
        """
        self._id = uid
        self._signature_service = SignatureService(uid)
        self._threshold_encryption_service = ThresholdEncryptionService(
            'thenc8_2.keys', uid)
        self._secrets_db = SecretsDB('databases/secrets' + str(uid) + 'db')
        self._N = CONSTANTS.N
        self._f = CONSTANTS.f
        self._state_machines = {}

        PORTS = xrange(8001, 8001 + CONSTANTS.N)
        from messaging_service import MessagingService, Address
        ADDRESSES = [Address(port - 8001, port, 'localhost', True) for
                     port in PORTS]
        ADDRESSES += [Address(7, 8001 + CONSTANTS.N, 'localhost', False)]
        self._messaging_service = MessagingService(ADDRESSES, self)
        asyncore.loop()

    def handle_message(self, msg):
        if not msg.verify_signatures(self._signature_service):
            return

        if (isinstance(msg, GetMessage) or
                isinstance(msg, DecryptionShareMessage)):
            key = (msg.key, msg.timestamp, "GET")
            if key not in self._state_machines:
                self._state_machines[key] = GetStateMachine(msg, self)
            self._state_machines[key].handle_message(msg)
        elif isinstance(msg, PutMessage) or isinstance(msg, PutAcceptMessage):
            key = (msg.key, msg.timestamp, "PUT")
            if key not in self._state_machines:
                self._state_machines[key] = PutStateMachine(msg, self)
            self._state_machines[key].handle_message(msg)

    @property
    def id(self):
        return self._id

    @property
    def port(self):
        return self.id + 8001

    @property
    def hostname(self):
        return 'localhost'

    @property
    def messaging_service(self):
        return self._messaging_service

    @property
    def threshold_encryption_service(self):
        return self._threshold_encryption_service

    @property
    def signature_service(self):
        return self._signature_service

    @property
    def write_ahead_log(self):
        pass

    @property
    def secrets_db(self):
        return self._secrets_db

    @property
    def catchup_state_machine(self):
        pass

    @property
    def f(self):
        return self._f

    @property
    def N(self):
        return self._N

if __name__ == '__main__':
    Server(1)
