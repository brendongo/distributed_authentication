import abc

from message import DecryptionShareMessage
from message import GetMessage
from message import PutMessage
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
        assert type(client_msg) is PutMessage

        self._acceptances = []  # List[server_id]
        self._client_msg = client_msg
        self._server = server
        self._sent_accept = False
        self._sent_response = False

    def _broadcast_put_accept(self):
        put_accept_msg = PutAcceptMessage(
            self._client_msg,
            self._server.id,
            self._server.signature_service
        )
        self._server.messaging_service.broadcast(put_accept_msg)

    def _enough_accepts(self):
        return len(self._acceptances) >= (2 * self._server.f + 1)

    def _store_secret(self):
        encrypted = self._server.threshold_encryption_service.encrypt(
            self._client_msg.secret
        )
        self._server.secrets_db.put(self._client_msg.key, encrypted)

    def _send_put_complete(self):
        put_complete_msg = PutCompleteMessage(
            self._server.id,
            self._server.signature_service
        )
        self._server.messaging_service.send(
            put_complete_msg,
            self._client_msg.client_id
        )

    def handle_message(self, message):
        assert type(message) is PutMessage or type(message) is PutAcceptMessage
        assert message.verify_signatures(self._server.signature_service)

        # Broadcast put_accept once
        if not self._sent_accept:
            self._broadcast_put_accept()
            self._acceptances.append(self._server.id)
            self._sent_accept = True

        if (type(message) is PutAcceptMessage and
                message.sender_id not in self._acceptances):

            self._acceptances.append(message.sender_id)

            if not self._sent_response and self._enough_accepts():
                self._store_secret()
                self._send_put_complete()
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

    def _broadcast_decryption_share(self):
        self._encrypted = self._server.secrets_db.get(self._client_msg.key)
        decryption_share = self._server.threshold_encryption_service.decrypt(
            self._encrypted
        )
        decryption_share_msg = DecryptionShareMessage(
            decryption_share,
            self._server.id,
            self._client_msg,
            self._server.signature_service
        )
        self._server.messaging_service.broadcast(decryption_share_msg)

    def _enough_shares(self):
        return len(self._decryption_shares) >= (2 * self._server.f + 1)

    def _send_response_message(self):
        secret = self._server.threshold_encryption_service.combine_shares(
            self._encrypted,
            self._decryption_shares,
            self._heard_servers
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

    def handle_message(self, message):
        assert (type(message) is GetMessage or
                type(message) is DecryptionShareMessage)
        assert (message.verify_signature(self._server.signature_service))

        if not self._sent_share:
            self._broadcast_decryption_share()
            self._sent_share = True

            # Add own share to share list
            self._decryption_shares.append(decryption_share)
            self._heard_servers.append(self._server.id)

        if message.sender_id not in self._heard_servers:
            self._decryption_shares.append(message.decryption_share)
            self._heard_servers.append(message.sender_id)

            if not self._sent_response and self._enough_shares():
                self._send_response_message()
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
    from pake2plus.util import number_to_bytes, bytes_to_number
    servers = [StubServer(i) for i in [0, 1, 2, 3, 4, 5]]

    secret = 4720180751612715235271090812360374322170044808629075413983095821158821133441
    secret = str(number_to_bytes(secret, 2 ** 256 - 1))
    encrypted = servers[0].threshold_encryption_service.encrypt(secret)

    client_msg = PutMessage("brendon", secret, 1001, servers[0].signature_service)
    put_state_machine = PutStateMachine(client_msg, servers[0])

    for i in xrange(6):
        put_accept_msg = PutAcceptMessage(
            client_msg, i, servers[0].signature_service
        )
        print "Send Put ", i
        put_state_machine.handle_message(put_accept_msg)

    print ""

    client_msg = GetMessage("brendon", 1001, servers[0].signature_service)

    get_state_machine = GetStateMachine(client_msg, servers[0])

    for i in xrange(6):
        decryption_share = servers[i].threshold_encryption_service.decrypt(encrypted)
        decryption_share_msg = DecryptionShareMessage(
            decryption_share,
            servers[i].id,
            client_msg,
            servers[i].signature_service
        )
        print "Send Decryption Share", i
        get_state_machine.handle_message(decryption_share_msg)


