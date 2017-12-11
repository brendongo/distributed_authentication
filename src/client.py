import argparse
import asyncore
import message
import socket
import threading
from state_machine import ClientGetStateMachine, ClientPutStateMachine
from state_machine import LameClientGetStateMachine, LameClientPutStateMachine
from messaging_service import MessagingService, Address
from message import LoginRequest
from message import LoginResponse
from message import EnrollRequest
from message import EnrollResponse
from signature_service import get_signature_service
from pake2plus.pake2plus import password_to_secret_A
from pake2plus.pake2plus import SPAKE2PLUS_A
from utils import CONSTANTS
from timer import Timer
from lamedb import LameSecretsDB


class ApplicationClient(object):
    def __init__(self, server_ports, client_id):
        self._state_machines = {}

        self._signature_service = get_signature_service()(client_id)
        self._id = client_id

        ADDRESSES = [Address(port - 8001, port, 'localhost', True) for
                     port in xrange(8001, 8001 + CONSTANTS.N)]
        ADDRESSES += [Address(100, 8001 + CONSTANTS.N, 'localhost', False)]
        self._messaging_service = MessagingService(ADDRESSES, self)

        self._datastore = LameSecretsDB()
        asyncore.loop()


    @property
    def datastore(self):
        return self._datastore

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
    def f(self):
        return 2

    @property
    def signature_service(self):
        return self._signature_service

    @property
    def messaging_service(self):
        return self._messaging_service

    def handle_message(self, msg):
        #if not msg.verify_signatures(self._signature_service):
        #    print "Welp, fuck"
        #    return

        if CONSTANTS.LAME_CLIENT:
            if isinstance(msg, message.LoginRequest):
                key = (msg.username, msg.timestamp, "LOGIN")
                state_machine = self._state_machines[key] = \
                    LameClientGetStateMachine(msg, self)
            elif isinstance(msg, message.EnrollRequest):
                key = (msg.timestamp, "ENROLL")
                state_machine = self._state_machines[key] = \
                    LameClientPutStateMachine(msg, self)
            else:
                raise ValueError("Unhandled message: {}".format(msg))
            return


        if isinstance(msg, message.LoginRequest):
            key = (msg.username, msg.timestamp, "LOGIN")
            state_machine = self._state_machines[key] = \
                    ClientGetStateMachine(msg, self)
        elif isinstance(msg, message.EnrollRequest):
            key = (msg.timestamp, "ENROLL")
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
        #thread.daemon = True
        thread.start()  # Wheeeeeeeee

    @property
    def id(self):
        return 101

    @property
    def port(self):
        return 8102

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
        secretA = password_to_secret_A(password)
        SA = SPAKE2PLUS_A(secretA)
        u = SA.start()

        l = LoginRequest(username, u, self.id)
        self._callbacks[(username, l.timestamp)] = callback
        self._messaging_service.send(l, self._client_id)

    def enroll(self, username, password, callback):
        e = EnrollRequest(username, password, self.id)
        self._callbacks[(username, e.timestamp)] = callback
        self._messaging_service.send(e, self._client_id)

    def handle_message(self, msg):
        if isinstance(msg, LoginResponse) or isinstance(msg, EnrollResponse):
            self._callbacks[(msg.username, msg.timestamp)](msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("user", type=int)
    args = parser.parse_args()
    if args.user == 8:
        user = User(100)
        num_calls = 50
        timer = Timer(num_calls, "rsa")
        for i in xrange(num_calls):
            user.enroll(str(i), "bdon", timer.call)
    elif args.user == 7:
        client = ApplicationClient(None, 100)
