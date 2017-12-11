from os import path, listdir
from ecdsa import SigningKey, VerifyingKey, BadSignatureError
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from utils import CONSTANTS


CONFIG_DIR = "config"
CONFIG_SUFFIX = "_signature.config"
VK_STR_LEN = 48
SK_STR_LEN = 24


class SignatureService(object):
    def __init__(self, server_id):
        raise NotImplementedError

    def sign(self, msg):
        """Sign message with private key

        Args:
            msg (string)

        Returns:
            string
        """
        raise NotImplementedError

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
        raise NotImplementedError


class RSASignatureService(SignatureService):
    def __init__(self, server_id):
        all_config_filename = path.join(CONFIG_DIR, "rsakeys.pem")
        if not path.isfile(all_config_filename):
            # TODO all servers use the same private public key which is
            # fine for timing but is very insecure.
            key = RSA.generate(2048)
            f = open(all_config_filename, 'w')
            f.write(key.exportKey('PEM'))
            f.close()

        f = open(all_config_filename, 'r')
        self.key = RSA.importKey(f.read())

    def sign(self, msg):
        digest = SHA256.new(msg).digest()
        signature = self.key.sign(digest, '')[0]
        return str(signature)

    def validate(self, msg, sender, signature):
        signature = (long(signature),)
        digest = SHA256.new(msg).digest()
        return self.key.publickey().verify(digest, signature)


class NoSignatureService(SignatureService):
    def __init__(self, server_id):
        pass

    def sign(self, msg):
        return ""

    def validate(self, msg, sender, signature):
        return True


class ECDSASignatureService(SignatureService):
    sk = None

    def __init__(self, server_id):
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
                other_server_id = int(filename[0:len(filename) - len(CONFIG_SUFFIX)])
                with open(path.join(CONFIG_DIR, filename)) as config_file:
                    self.vks[other_server_id] = VerifyingKey.from_string(
                                                    config_file.read(VK_STR_LEN))
                    # Remember your own secret key
                    if other_server_id == server_id:
                        self.sk = SigningKey.from_string(
                                    config_file.read(SK_STR_LEN))

        assert self.sk # Make sure that you know your own secret key

    def sign(self, msg):
        return self.sk.sign(msg).encode('base64')

    def validate(self, msg, sender, signature):
        signature = signature.decode('base64')
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


def get_signature_service():
    if CONSTANTS.SIGNATURE_SERVICE == "rsa":
        return RSASignatureService
    elif CONSTANTS.SIGNATURE_SERVICE == "ecdsa":
        return ECDSASignatureService
    elif CONSTANTS.SIGNATURE_SERVICE == "none":
        return NoSignatureService
    else:
        raise ValueError("Unsupported signature service")

if __name__ == '__main__':
    ss1 = RSASignatureService(1)
    signature1 = ss1.sign("hello world")
    assert ss1.validate("hello world", 1, signature1)

    ss2 = RSASignatureService(2)
    signature2 = ss2.sign("yellow red")
    assert ss1.validate("yellow red", 2, signature2)
    assert not ss1.validate("yellow", 2, signature2)
    assert not ss1.validate("yellow red", 2, signature1)
    assert ss2.validate("hello world", 2, signature1)

    print "Passes"
