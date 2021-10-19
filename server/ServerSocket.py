from struct import pack, unpack
import socket
import pickle

MAX_LEN = 4096
HEADER_SIZE = 8


class ServerSocket(socket.socket):
    def __init__(self, *args, **kwargs):
        super(ServerSocket, self).__init__(*args, **kwargs)
        self.client = None
        self.client_addr = None

    def accept(self):
        self.client, self.client_addr = super(ServerSocket, self).accept()
        return self.client_addr

    def receive_signal(self):
        assert self.client != None
        try:
            s = self.client.recv(MAX_LEN).decode("utf8").rstrip()
            if s == "":
                s = "QUIT"

        except:
            s = "QUIT"

        finally:
            return s

    def send_signal(self, msg):
        assert self.client != None
        self.client.sendall(bytes(msg, "utf8"))

    def receive_obj(self):
        assert self.client != None
        msg = bytearray()
        header = self.client.recv(HEADER_SIZE)
        (length,) = unpack(">Q", header)
        length_recv = 0
        while length_recv < length:
            s = self.client.recv(MAX_LEN)
            msg += s
            length_recv += len(s)
        return pickle.loads(msg)

    def send_obj(self, obj):
        assert self.client != None
        msg = pickle.dumps(obj)
        length = pack(">Q", len(msg))
        self.client.sendall(length)
        self.client.sendall(msg)

    def close(self):
        assert self.client != None
        self.client.shutdown(socket.SHUT_RDWR)
        self.client.close()
        super(ServerSocket, self).close()
