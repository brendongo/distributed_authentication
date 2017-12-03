import socket
import message
from state_machine import ClientGetStateMachine, ClientPutStateMachine
from messaging_service import MessagingService, Address


class ApplicationClient(object):
    def __init__(self, server_ports, signature_service, client_id):
        self._state_machines = {}

        server_ports = [8001, 8002, 8003]
        ADDRESSES = [Address(port - 8001, port, 'localhost', True)] for
                     port in xrange(8001, 8008)]
        ADDRESSES += [Address(7, 8008, 'localhost', False)]
        self._messaging_service = MessagingService(ADDRESSES, self)
        asyncore.loop()

    @property
    def id(self):
        return 7

    @property
    def port(self):
        return 8008

    @property
    def hostname(self):
        return 'localhost'

    def handle_message(self, msg):
        if not msg.verify_signatures(self._signature_service):
            return

        if isinstance(msg, message.LoginRequest):
            key = (msg.username, msg.timestamp, "LOGIN")
            state_machine = self._state_machines[key] = \
                    ClientGetStateMachine(msg, self)
            state_machine.handle_message(msg)
        elif isinstance(msg, message.EnrollRequest):
            key = (msg.username, msg.timestamp, "ENROLL")
            state_machine = self._state_machines[key] = \
                    ClientPutStateMachine(msg, self)
            state_machine.handle_message(msg)
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
    def __init__(self, application_client_port):

        #self._messaging_service = MessagingService()
        #Thread(asyncore.loop()) # blocks

    def login(self, username, callback):
        # Make a call to MessagingService, send a GetRequest to ApplicationClient
        # Returns immediately

        # Assign request an id, put it in the msg
        #self._callbacks[transaction_id] = callback
        pass

    def enroll(self, username, password, callback):
        pass

    def handle_message(self, msg):
        #if msg.type == "GET":
        #    self._callbacks[msg.transaction_id](msg.value)
        #else:
        #    self._callbacks[msg.transaction_id]()

user = User()
for _ in xrange(10000):
    user.put("bdon", _, timer_callback)

for _ in xrange(10000):
    user.get("bdon", timer_callback)
