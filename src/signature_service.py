class SignatureService(object):
    def __init__(self, private_key, public_keys):
        """
        Args:
            private_key (type):
            public_keys (list[(id, public_key)])
        """
        pass

    def sign(self, msg):
        """Sign message with private key

        Args:
            msg (string)

        Returns:
            string
        """
        pass

    def validate(self, msg, sender, signature):
        """Validate signature on message

        Args:
            msg (string)
            sender_id (int)
            signature (string)

        Returns:
            bool
        """
        pass
