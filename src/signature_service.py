class SignatureService(object):
    def __init__(self, keys_filename):
        """
        Args:
            keys_filename (string): filename of file that contains private key
            and public keys of other servers and clients
        """
        pass

    def sign(msg):
        """Sign message with private key

        Args:
            msg (string)

        Returns:
            string
        """
        pass

    def validate(msg, sender, signature):
        """Validate signature on message

        Args:
            msg (string)
            sender_id (int)
            signature (string)

        Returns:
            bool
        """
        pass
