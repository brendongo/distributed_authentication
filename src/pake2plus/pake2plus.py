## FROM: https://github.com/warner/python-spake2/blob/master/src/spake2/spake2.py

import os, json
from binascii import hexlify, unhexlify
from hashlib import sha256
from params import _Params
from ed25519_group import Ed25519Group

DefaultParams = _Params(Ed25519Group)

class SPAKEError(Exception):
    pass
class OnlyCallStartOnce(SPAKEError):
    """start() may only be called once. Re-using a SPAKE2 instance is likely
    to reveal the password or the derived key."""
class OnlyCallFinishOnce(SPAKEError):
    """finish() may only be called once. Re-using a SPAKE2 instance is likely
    to reveal the password or the derived key."""
class OffSides(SPAKEError):
    """I received a message from someone on the same side that I'm on: I was
    expecting the opposite side."""
class SerializedTooEarly(SPAKEError):
    pass
class WrongSideSerialized(SPAKEError):
    """You tried to unserialize data stored for the other side."""
class WrongGroupError(SPAKEError):
    pass
class ReflectionThwarted(SPAKEError):
    """Someone tried to reflect our message back to us."""

SideA = b"A"
SideB = b"B"

# to serialize intermediate state, just remember x and A-vs-B. And M/N.

def finalize_SPAKE2PLUS(X_msg, Y_msg, K_bytes, d_bytes, pi_0):
    transcript = b"".join([sha256(pi_0).digest(),
                           X_msg, Y_msg, K_bytes, d_bytes])
    key = sha256(transcript).digest()
    return key

class _SPAKE2_Base(object):
    "This class manages one side of a SPAKE2 key negotiation."

    side = None # set by the subclass

    def __init__(self, secret, #unused in PAKE2PLUS
                 params=DefaultParams, entropy_f=os.urandom):
        assert len(secret) == 2

        self.pi_0_scalar = secret[0]

        assert isinstance(params, _Params), repr(params)
        self.params = params
        self.entropy_f = entropy_f

        self._started = False
        self._finished = False

    def start(self):
        if self._started:
            raise OnlyCallStartOnce("start() can only be called once")
        self._started = True

        g = self.params.group
        self.xy_scalar = g.random_scalar(self.entropy_f)
        self.xy_elem = g.Base.scalarmult(self.xy_scalar)
        self.compute_outbound_message()
        # Guard against both sides using the same side= by adding a side byte
        # to the message. This is not included in the transcript hash at the
        # end.
        outbound_side_and_message = self.side + self.outbound_message
        return outbound_side_and_message

    def compute_outbound_message(self):
        #message_elem = self.xy_elem + (self.my_blinding() * self.pw_scalar)
        pi_0_blinding = self.my_blinding().scalarmult(self.pi_0_scalar)
        message_elem = self.xy_elem.add(pi_0_blinding)
        self.outbound_message = message_elem.to_bytes()

    def finish(self, inbound_side_and_message):
        if self._finished:
            raise OnlyCallFinishOnce("finish() can only be called once")
        self._finished = True

        self.inbound_message = self._extract_message(inbound_side_and_message)

        g = self.params.group
        inbound_elem = g.bytes_to_element(self.inbound_message)
        if inbound_elem.to_bytes() == self.outbound_message:
            raise ReflectionThwarted
        
        pi_0_unblinding = self.my_unblinding().scalarmult(-self.pi_0_scalar)
        self.unblinded_message = inbound_elem.add(pi_0_unblinding)
        K_elem = self.unblinded_message.scalarmult(self.xy_scalar)
        return K_elem.to_bytes()

    # def hash_params(self):
    #     # We can't really reconstruct the group from static data, but we'll
    #     # record enough of the params to confirm that we're using the same
    #     # ones upon restore. Otherwise the failure mode is silent key
    #     # disagreement. Any changes to the group or the M/N seeds should
    #     # cause this to change.
    #     g = self.params.group
    #     pieces = [g.arbitrary_element(b"").to_bytes(),
    #               g.scalar_to_bytes(g.password_to_scalar(b"")),
    #               self.params.M.to_bytes(),
    #               self.params.N.to_bytes(),
    #               ]
    #     return sha256(b"".join(pieces)).hexdigest()

    def serialize(self):
        if not self._started:
            raise SerializedTooEarly("call .start() before .serialize()")
        return json.dumps(self._serialize_to_dict()).encode("ascii")

    @classmethod
    def from_serialized(klass, data, params=DefaultParams):
        d = json.loads(data.decode("ascii"))
        return klass._deserialize_from_dict(d, params)

class _SPAKE2_Asymmetric(_SPAKE2_Base):
    idA = b""
    idB = b""

    def _extract_message(self, inbound_side_and_message):
        other_side = inbound_side_and_message[0:1]
        inbound_message = inbound_side_and_message[1:]

        if other_side not in (SideA, SideB):
            raise OffSides("I don't know what side they're on")
        if self.side == other_side:
            if self.side == SideA:
                raise OffSides("I'm A, but I got a message from A (not B).")
            else:
                raise OffSides("I'm B, but I got a message from B (not A).")
        return inbound_message

    def _finalize(self, K_bytes, d_bytes):
        return finalize_SPAKE2PLUS(self.X_msg(), self.Y_msg(), K_bytes, d_bytes,
                                self.params.group.scalar_to_bytes(self.pi_0_scalar))

    # def _serialize_to_dict(self):
    #     g = self.params.group
    #     d = {"hashed_params": self.hash_params(),
    #          "side": self.side.decode("ascii"),
    #          "idA": hexlify(self.idA).decode("ascii"),
    #          "idB": hexlify(self.idB).decode("ascii"),
    #          "password": hexlify(self.pw).decode("ascii"),
    #          "xy_scalar": hexlify(g.scalar_to_bytes(self.xy_scalar)).decode("ascii"),
    #          }
    #     return d

    # @classmethod
    # def _deserialize_from_dict(klass, d, params):
    #     def _should_be_unused(count): raise NotImplementedError
    #     self = klass(password=unhexlify(d["password"].encode("ascii")),
    #                  idA=unhexlify(d["idA"].encode("ascii")),
    #                  idB=unhexlify(d["idB"].encode("ascii")),
    #                  params=params, entropy_f=_should_be_unused)
    #     if d["side"].encode("ascii") != self.side:
    #         raise WrongSideSerialized
    #     if d["hashed_params"] != self.hash_params():
    #         err = ("SPAKE2.from_serialized() must be called with the same"
    #                "params= that were used to create the serialized data."
    #                "These are different somehow.")
    #         raise WrongGroupError(err)
    #     g = self.params.group
    #     self._started = True
    #     xy_scalar_bytes = unhexlify(d["xy_scalar"].encode("ascii"))
    #     self.xy_scalar = g.bytes_to_scalar(xy_scalar_bytes)
    #     self.xy_elem = g.Base.scalarmult(self.xy_scalar)
    #     self.compute_outbound_message()
    #     return self

# applications should use SPAKE2_A and SPAKE2_B, not raw _SPAKE2_Base()

def password_to_secret_A(password, params=DefaultParams):
    return params.group.password_to_secret(password)

def password_to_secret_B(password, params=DefaultParams):
    pi_0, pi_1 = password_to_secret_A(password, params)
    return (pi_0, params.group.Base.scalarmult(pi_1).to_bytes())

class SPAKE2PLUS_A(_SPAKE2_Asymmetric):
    "Client"
    side = SideA 

    def __init__(self, secret): # a tuple pair
        super(SPAKE2PLUS_A, self).__init__(secret)
        self.pi_1_scalar = secret[1]

    def finish(self, inbound_side_and_message):
        K_bytes = super(SPAKE2PLUS_A, self).finish(inbound_side_and_message)

        # PAKE 2+: Calculate additional value d
        d_bytes = self.unblinded_message.scalarmult(self.pi_1_scalar).to_bytes()

        key = self._finalize(K_bytes, d_bytes)
        return key 

    def my_blinding(self): return self.params.M
    def my_unblinding(self): return self.params.N
    def X_msg(self): return self.outbound_message
    def Y_msg(self): return self.inbound_message

class SPAKE2PLUS_B(_SPAKE2_Asymmetric):
    "Server"
    side = SideB

    def __init__(self, secret): # a tuple pair
        super(SPAKE2PLUS_B, self).__init__(secret)
        self.c = self.params.group.bytes_to_element(secret[1])

    def finish(self, inbound_side_and_message):
        K_bytes = super(SPAKE2PLUS_B, self).finish(inbound_side_and_message)

        # PAKE 2+: Calculate additional value d
        d_bytes = self.c.scalarmult(self.xy_scalar).to_bytes()

        key = self._finalize(K_bytes, d_bytes)
        return key

    def my_blinding(self): return self.params.N
    def my_unblinding(self): return self.params.M
    def X_msg(self): return self.inbound_message
    def Y_msg(self): return self.outbound_message

# add ECC version for smaller messages/storage
# consider timing attacks
# try for compatibility with Boneh's JS version