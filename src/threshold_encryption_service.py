import tpke


class ThresholdEncryptionService(object):
    def __init__(self, keys_file, server_id):
        """
        Args:
            keys_file (string): filename of file with threshold encryption keys
            server_id (int): id of the server
        """
        self._server_id = server_id
        encPK, encSKs = tpke.initiateThresholdEnc(keys_file)
        self._encryp_key = encPK
        self._secret_key = encSKs[server_id]

    def encrypt(self, msg):
        """Takes a message and returns something.

        Args:
            msg (string): message we want to encrypt
            limited to 32 bytes

        Return:
            opaque object used by threshold decryption and combine shares

        """
        U, V, W = self._encryp_key.encrypt(msg)
        return (U, V, None)

    def decrypt(self, msg):
        """Takes decryption_shares and turns it into a message.

        Args:
            opaque object returned by encrypt

        Returns:
            opaque object used by threshold combine shares
        """
        return self._secret_key.decrypt_share(msg)

    def combine_shares(self, encrypted, decryption_shares, server_ids):
        """Combines encrypted object and decryption shares to get
        original message

        Args:
            encrypted (opaque object returned by encrypt)
            decryption_shares list[(opaque object returned by decrypt)]
            server_ids (list[int]): ids of servers that returned decryption
            shares must have one to one correspondence with decryption_shares

        Return:
            string
        """
        k = self._encryp_key.k
        decryption_shares = decryption_shares[:k]
        server_ids = server_ids[:k]
        shares = dict(zip(server_ids, decryption_shares))
        msg = self._encryp_key.combine_shares(encrypted, shares)
        return msg


if __name__ == '__main__':

    from pake2plus.pake2plus import (
      SPAKE2PLUS_A,
      SPAKE2PLUS_B,
      password_to_secret_A,
      password_to_secret_B,
      )
    from pake2plus.groups import password_to_scalar
    from pake2plus.util import number_to_bytes, bytes_to_number

    # Generate the secrets
    secretA = password_to_secret_A(b"hello world")
    secretB = password_to_secret_B(b"hello world")

    # Store this
    pi_0_str = str(number_to_bytes(secretB[0], 2 ** (256) - 1))
    # Retrieve pi_0 as string of bytes then convert back to long
    pi_0 = bytes_to_number(pi_0_str)

    # Store this
    c = secretB[1]


    assert pi_0 == secretB[0]

    m = secretB[1]

    service0 = ThresholdEncryptionService('thenc8_2.keys', 0)
    service1 = ThresholdEncryptionService('thenc8_2.keys', 1)
    service2 = ThresholdEncryptionService('thenc8_2.keys', 3)
    service3 = ThresholdEncryptionService('thenc8_2.keys', 5)
    # m = b"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

    e0 = service0.encrypt(m)
    e1 = service0.encrypt(m)
    e2 = service2.encrypt(m)
    e3 = service3.encrypt(m)

    assert e1 == e2
    assert e2 == e3

    d0 = service0.decrypt(e1)
    d1 = service1.decrypt(e1)
    d2 = service2.decrypt(e1)
    d3 = service3.decrypt(e1)

    assert d0 != d1
    assert d0 != d2
    assert d0 != d3
    assert d1 != d2
    assert d2 != d3
    assert d1 != d3

    m_ = service1.combine_shares(e2, [d0, d1, d2, d3], [0, 1, 3, 5])
    assert m_ == m

    # Perform the key exchange and verify that both have obtained the same key
    SA = SPAKE2PLUS_A(secretA)
    SB = SPAKE2PLUS_B(secretB)

    msg_outA = SA.start()
    msg_outB = SB.start()

    msg_inA = msg_outB
    msg_inB = msg_outA

    assert SA.finish(msg_inA) == SB.finish(msg_inB)
    print "Passes"