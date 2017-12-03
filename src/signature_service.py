from os import path, listdir
from ecdsa import SigningKey, VerifyingKey, BadSignatureError

CONFIG_DIR = "config"
CONFIG_SUFFIX = "_signature.config"
VK_STR_LEN = 48
SK_STR_LEN = 24

class SignatureService(object):
    sk = None

    def __init__(self, server_id):
        """
        Args:
            id (int):
        """ 
        # Create your own config file if it doesn't exist 
        self.server_id = server_id
        own_config_filename = path.join(CONFIG_DIR, str(server_id) + CONFIG_SUFFIX)
        if not path.isfile(own_config_filename):
            sk = SigningKey.generate()
            vk = sk.get_verifying_key()
            with open(own_config_filename, "w") as config_file:
                config_file.write(vk.to_string())
                config_file.write(sk.to_string())

        # Look for all config files in the directory
        self.vks = {}
        for filename in listdir(CONFIG_DIR):
            if filename.endswith(CONFIG_SUFFIX):
                other_server_id = int(filename[0])
                with open(path.join(CONFIG_DIR, filename)) as config_file:
                    self.vks[other_server_id] = VerifyingKey.from_string(
                                                    config_file.read(VK_STR_LEN))
                    # Remember your own secret key
                    if other_server_id == server_id:
                        self.sk = SigningKey.from_string(
                                    config_file.read(SK_STR_LEN))

        assert self.sk # Make sure that you know your own secret key

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
        # If we do not have the sender on file, look for their config file
        return True
        if sender not in self.vks:
            sender_config_filename = path.join(CONFIG_DIR, str(sender) + CONFIG_SUFFIX)
            if path.isfile(sender_config_filename):
                with open(sender_config_filename) as config_file:
                    self.vks[sender] = VerifyingKey.from_string(
                                            config_file.read(VK_STR_LEN))
            else:
                print ("Server %r cannot find server %r in signature config files."
                        %(self.server_id, sender))
                return False

        # Perform validation
        vk = self.vks[sender]
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

