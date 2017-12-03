from os import path
from ecdsa import SigningKey, VerifyingKey, BadSignatureError

CONFIG_DIR = "config"
CONFIG_SUFFIX = "_signature.config"
VK_STR_LEN = 48
SK_STR_LEN = 24

class SignatureService(object):
    def __init__(self, server_id):
        """
        Args:
            id (int):
        """ 
        self.config_filename = path.join(CONFIG_DIR, str(server_id) + CONFIG_SUFFIX)

        if not path.isfile(self.config_filename):
            sk = SigningKey.generate()
            vk = sk.get_verifying_key()
            with open(self.config_filename, "w") as config_file:
                config_file.write(vk.to_string())
                config_file.write(sk.to_string())

        with open(self.config_filename) as config_file:
            self.vk = VerifyingKey.from_string(
                        config_file.read(VK_STR_LEN))
            self.sk = SigningKey.from_string(
                        config_file.read(SK_STR_LEN))

    def sign(self, msg):
        """Sign message with private key

        Args:
            msg (string)

        Returns:
            string
        """
        return self.sk.sign(msg)

    def validate(self, msg, sender, signature):
        """Validate signature on message

        Args:
            msg (string)
            sender_id (int)
            signature (string)

        Returns:
            bool
        """
        sender_config_filename = path.join(CONFIG_DIR, str(sender) + CONFIG_SUFFIX)
        if not path.isfile(sender_config_filename):
            return False

        with open(sender_config_filename) as sender_config_file:
            vk = VerifyingKey.from_string(sender_config_file.read(VK_STR_LEN))
            try:
                vk.verify(signature, msg)
            except BadSignatureError:
                return False
            return True

# TEST CODE

####
# ss1 = SignatureService(1)
# signature1 = ss1.sign("hello world")
# print ss1.validate("hello world", 1, signature1)

# ss2 = SignatureService(2)
# signature2 = ss2.sign("yellow red")
# print ss1.validate("yellow red", 2, signature2)
# print ss1.validate("yellow", 2, signature2)
# print ss1.validate("yellow red", 2, signature1)

