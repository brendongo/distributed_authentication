import json
import struct
from message import Message, IntroMessage

class Buffer(object):
    def __init__(self):
        self._buffer = ""
        self._next_length = None

    @property
    def next_length(self):
        if self._next_length is not None:
            return self._next_length

        if len(self._buffer) >= 4:
            length, = struct.unpack(
                    '!I', self._buffer[:4])
            self._buffer = self._buffer[4:]
            self._next_length = length
            return length
        else:
            return None

    def write_to(self, data):
        self._buffer += data

    def read_from(self):
        length = self.next_length
        if length is not None and len(self._buffer) >= length:
            data = self._buffer[:length]
            self._buffer = self._buffer[length:]
            msg = Message.from_json(json.loads(data))
            self._next_length = None
            return msg
        else:
            return None
