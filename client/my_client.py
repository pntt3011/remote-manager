from struct import pack, unpack
import socket
import pickle

# Chua xu li ket noi bi ngat dot ngot

PORT = 8080
BUFFER_SIZE = 4096
HEADER_SIZE = 8

class Client(socket.socket):
    def __init__(self, UI_control, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.UI_control = UI_control

    def connect(self, server_ip_address):
        server_address = (server_ip_address, PORT)
        super().connect(server_address)

    def send_signal(self, msg):
        try:
            self.send_obj(msg)
            return True
        except:
            self.UI_control.lost_connection_handle()
            return False

    def receive_signal(self):
        try:
            return self.receive_obj()
        except:
            self.UI_control.lost_connection_handle()
            return None

    def send_obj(self, obj):
        msg = pickle.dumps(obj)
        length = pack('>Q', len(msg))
        try:
            self.sendall(length)
            self.sendall(msg)
            return True
        except:
            self.UI_control.lost_connection_handle()
            return False

    def receive_obj(self):
        msg = bytearray()
        header = self.recv(HEADER_SIZE)
        (length,) = unpack('>Q', header)

        length_recv = 0
        while length_recv < length:
            try:
                s = self.recv(min(BUFFER_SIZE, length_recv))
            except:
                self.UI_control.lost_connection_handle()
                return None
            msg += s
            length_recv += len(s)

        return pickle.loads(msg)