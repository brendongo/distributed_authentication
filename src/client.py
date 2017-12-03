import argparse
import asyncore
import message
import socket
import threading
from state_machine import ClientGetStateMachine, ClientPutStateMachine
from messaging_service import MessagingService, Address
from message import LoginRequest
from message import EnrollRequest
from signature_service import SignatureService


class ApplicationClient(object):
    def __init__(self, server_ports, client_id):
        self._state_machines = {}

        self._signature_service = SignatureService(client_id)
        self._id = client_id

        ADDRESSES = [Address(port - 8001, port, 'localhost', True) for
                     port in xrange(8001, 8008)]
        ADDRESSES += [Address(7, 8008, 'localhost', False)]
        self._messaging_service = MessagingService(ADDRESSES, self)
        asyncore.loop()

    @property
    def id(self):
        return self._id

    @property
    def port(self):
        return self._id + 8001

    @property
    def hostname(self):
        return 'localhost'

    @property
    def signature_service(self):
        return self._signature_service

    @property
    def messaging_service(self):
        return self._messaging_service

    def handle_message(self, msg):
        if not msg.verify_signatures(self._signature_service):
            return

        if isinstance(msg, message.LoginRequest):
            key = (msg.username, msg.timestamp, "LOGIN")
            state_machine = self._state_machines[key] = \
                    ClientGetStateMachine(msg, self)
        elif isinstance(msg, message.EnrollRequest):
            key = (msg.username, msg.timestamp, "ENROLL")
            state_machine = self._state_machines[key] = \
                    ClientPutStateMachine(msg, self)
        elif isinstance(msg, message.GetResponseMessage):
            key = (msg.get_msg.key, msg.get_msg.timestamp, "LOGIN")
            state_machine = self._state_machines[key]
            assert state_machine
            state_machine.handle_message(msg)
        elif isinstance(msg, message.PutCompleteMessage):
            key = (msg.put_msg.timestamp, "ENROLL")
            state_machine = self._state_machines[key]
            assert state_machine
            state_machine.handle_message(msg)
        else:
            raise ValueError("Unhandled message: {}".format(msg))


class User(object):
    def __init__(self, client_id):
        self._callbacks = {}
        self._client_id = client_id
        ADDRESSES = [Address(client_id, client_id + 8001, 'localhost', True)]
        self._messaging_service = MessagingService(ADDRESSES, self)

        thread = threading.Thread(target=asyncore.loop)
        thread.daemon = True
        thread.start()  # Wheeeeeeeee

    @property
    def id(self):
        return 8

    @property
    def port(self):
        return 8009

    @property
    def hostname(self):
        return 'localhost'

    @property
    def signature_service(self):
        return self._signature_service

    @property
    def messaging_service(self):
        return self._messaging_service

    def login(self, username, password, callback):
        # Make a call to MessagingService, send a GetRequest to
        # ApplicationClient
        # Returns immediately

        # Assign request an id, put it in the msg
        #self._callbacks[transaction_id] = callback
        u = 0
        l = LoginRequest(username, u, self.id)
        self._callbacks[(username, l.timestamp)] = callback
        self._messaging_service.send(l, self._client_id)

    def enroll(self, username, password, callback):
        e = EnrollRequest(username, password, self.id)
        self._callbacks[(username, e.timestamp)] = callback
        self._messaging_service.send(e, self._client_id)

    def handle_message(self, msg):
        if isinstance(msg, LoginResponse):
            self._callbacks[(msg.username, msg.timestamp)](msg)
        #if msg.type == "GET":
        #    self._callbacks[msg.transaction_id](msg.value)
        #else:
        #    self._callbacks[msg.transaction_id]()


def printo(msg):
    print msg.to_json()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("user", type=int)
    args = parser.parse_args()
    print args
    if args.user == 8:
        user = User(7)
        import time
        time.sleep(1)
        user.enroll("bdon", "bdon", printo)
    elif args.user == 7:
        client = ApplicationClient(None, 7)
