from BaseSocket import BaseSocket
from struct import pack, unpack
import pickle

# Chua xu li ket noi bi ngat dot ngot

PORT = 8080
MAX_LEN = 8192
MAX_TRANSFER = 1024 * 256
HEADER_SIZE = 8


class Client(BaseSocket):
    def __init__(self, UI_control, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.UI_control = UI_control
        self.client = None
        self.client_addr = None
        self.transfer_send = None
        self.transfer_receive = None
        self.transfer_result = None
        self.monitor_window = None
        self.display = False

    def connect(self, server_ip_address):
        server_address = (server_ip_address, PORT)
        super().connect(server_address)
        self.client = self
        self.client_addr = server_ip_address

    def close(self):
        super().close()

    def set_root_window(self, tk):
        self.root_tk = tk

    def accept(self):
        self.client, addr = super(Client, self).accept()
        self.client_addr = addr[0]

    def receive_obj(self):
        try:
            msg = bytearray()
            header = self.client.recv(HEADER_SIZE)
            (length,) = unpack(">Q", header)
            while length > 0:
                s = self.client.recv(min(MAX_LEN, length))
                msg += s
                length -= len(s)
            return pickle.loads(msg)

        except:
            self.UI_control.handle_lost_connection()
            return None

    def send_obj(self, obj):
        try:
            msg = pickle.dumps(obj)
            length = pack(">Q", len(msg))
            self.client.sendall(length)
            self.client.sendall(msg)
            return True

        except:
            self.UI_control.handle_lost_connection()
            return False
