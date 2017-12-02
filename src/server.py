class Server(object):
    def __init__(self, config_filename):
        """
        Args:
            config_filename (string): contains threshold encryption keys,
                signature private key, signature public keys, location info
                about servers, server id
        """
        pass

    def handle_message(self, msg):
        pass

    @property
    def id(self):
        pass

    @property
    def port(self):
        pass

    @property
    def host(self):
        pass

    @property
    def messaging_service(self):
        pass

    @property
    def threshold_encryption_service(self):
        pass

    @property
    def signature_service(self):
        pass

    @property
    def write_ahead_log(self):
        pass

    @property
    def secrets_log(self):
        pass

    @property
    def catchup_state_machine(self):
        pass

    @property
    def f(self):
        pass

    @property
    def N(self):
        pass


