import abc

from message import DecryptionShareMessage
from message import GetMessage
from message import PutAcceptMessage
from message import PutCompleteMessage
from message import ResponseMessage


class StateMachine(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def handle_message(self, message):
        raise NotImplementedError()


class PutStateMachine(object):
    """State for put

    Args:
        client_msg (PutMessage)
        server (Server)
    """
    def __init__(self, client_msg, server):
        self._acceptances = []  # List[server_id]
        self._client_msg = client_msg
        self._server = server
        self._sent_accept = False
        self._sent_response = False

    def handle_message(self, message):
        if not self._sent_accept:
            put_accept_msg = PutAcceptMessage(
                self._client_msg,
                self._server.id,
                self._server.signature_service
            )
            self._server.messaging_service.broadcast(put_accept_msg)
            self._sent_accept = True

        if message.sender_id not in self._acceptances:
            self._acceptances.append(message.sender_id)

            if (not self._sent_response and
                    len(self._acceptances) >= (2 * self._server.f + 1)):

                encrypted = self._server.threshold_encryption_service.encrypt(
                    self._client_msg.secret
                )
                self._server.secret_db.put(encrypted)
                put_complete_msg = PutCompleteMessage(
                    self._server.id,
                    self._sender.signature_service
                )
                self._server.messaging_service.send(
                    put_complete_msg,
                    self._client_msg.sender_id
                )

                self._sent_response = True

            # TODO Send ACK


class GetStateMachine(object):
    def __init__(self, client_msg, server):
        """State for get

        Args:
            client_msg (GetMessage): message that this is handling
            server (Server)
        """
        assert type(client_msg) is GetMessage

        self._sent_share = False
        self._client_msg = client_msg
        self._server = server
        self._heard_servers = []  # List of server_ids heard from
        self._decryption_shares = []  # List of decryption_shares
        self._sent_response = False

    def handle_message(self, message):
        if not self._sent_share:
            decryption_share = ""
            decryption_share_msg = DecryptionShareMessage(
                decryption_share,
                self._server.id,
                self._client_msg,
                self._server.signature_service
            )
            self._server.messaging_service.broadcast(decryption_share_msg)
            self._sent_share = True

            # Add own share to share list
            self._decryption_shares.append(decryption_share)
            self._heard_servers.append(self._server.id)

        if message.sender_id not in self._heard_servers:
            self._decryption_shares.append(message.decryption_share)
            self._heard_servers.append(message.sender_id)

            if (not self._sent_response and
                    len(self._decryption_shares) >= (2 * self._server.f + 1)):

                secret = self._server.threshold_encryption_service.decrypt(
                    self._decryption_shares
                )

                response_message = ResponseMessage(
                    secret,
                    self._server.id,
                    self._server.signature_service
                )

                self._server.messaging_service.send(
                    response_message,
                    self._client_msg.client_id
                )

                self._sent_response = True
                # TODO Cleanup
            # TODO Ack message


class CatchupStateMachine(object):
    def __init__(self, server):
        """State for catching up on messages that haven't been seen before

        Args:
            server (Server)
        """
        self._catching_up = False  # Can False when you hear from 2f + 1
        self._entries = []
        self._servers = []

    def catch_up(self):
        pass

    def handle_message(self, message):
        pass


if __name__ == '__main__':
    from stubs import *
    server = StubServer()

    client_msg = GetMessage("user", 1001, server.signature_service)

    get_state_machine = GetStateMachine(client_msg, server)

    for i in xrange(6):
        decryption_share = ""
        decryption_share_msg = DecryptionShareMessage(
            decryption_share,
            i,
            client_msg,
            server.signature_service
        )
        print "Send ", i
        get_state_machine.handle_message(decryption_share_msg)

