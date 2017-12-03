from signature_service import SignatureService
from threshold_encryption_service import ThresholdEncryptionService
from signature_service import SignatureService
from secrets_db import SecretsDB


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
            'thenc8_2.keys',
            uid
        )
        self._secrets_db = SecretsDB('secrets' + str(uid) + 'db')
        self._N = 7
        self._f = 2


    def handle_message(self, msg):
        pass

    @property
    def id(self):
        return self._id

    @property
    def port(self):
        pass

    @property
    def hostname(self):
        pass

    @property
    def messaging_service(self):
        pass

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
    def secrets_log(self):
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
