from struct import pack, unpack
import socket
import pickle
import os

MAX_LEN = 8192
MAX_TRANSFER = 1024 * 256
HEADER_SIZE = 8


class ServerSocket(socket.socket):
    def __init__(self, *args, **kwargs):
        super(ServerSocket, self).__init__(*args, **kwargs)
        self.client = None
        self.client_addr = None
        self.transfer_send = None
        self.transfer_receive = None
        self.transfer_result = None
        self.monitor_window = None

    def connect(self, address):
        super(ServerSocket, self).connect(address)
        self.client = self
        self.client_addr = address[0]

    def accept(self):
        self.client, addr = super(ServerSocket, self).accept()
        print(addr)
        self.client_addr = addr[0]
        return self.client_addr

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
            return "QUIT"

    def send_obj(self, obj):
        try:
            msg = pickle.dumps(obj)
            length = pack(">Q", len(msg))
            self.client.sendall(length)
            self.client.sendall(msg)
            return True

        except:
            return False

    def start_transfer(self, path):
        if not self.send_obj(["RECEIVE", path]):
            return False

        if self.transfer_send is None:
            self.transfer_send = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.transfer_send.bind(('', 6969))
            self.transfer_send.listen(1)
            print("Start transfer")

        return True

    def end_transfer(self):
        try:
            self.transfer_send.close()
        except:
            pass
        finally:
            print("End transfer")
            self.transfer_send = None

    def receive_item(self, root):
        flag = True
        relpath = None

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.client_addr, 6969))

        with sock, sock.makefile('rb') as clientfile:
            while flag:
                raw = clientfile.readline()
                if not raw:
                    break

                try:
                    relpath = raw.strip().decode()
                    length = int(clientfile.readline())

                    path = os.path.join(root, relpath)

                    # Check if path exists
                    if os.path.exists(path):
                        self.send_obj(["DUPLICATE", path])
                        s = self.receive_obj()

                        if s[0] == "NO":
                            continue

                        if s[0] == "RENAME":
                            while True:
                                dir, name = os.path.split(path)
                                name = "Copy of " + name
                                path = os.path.join(dir, name)
                                if not os.path.exists(path):
                                    break
                    else:
                        self.send_obj(["NOT DUPLICATE"])

                    print(f"Receiving {path}")
                    os.makedirs(os.path.dirname(path), exist_ok=True)

                    # Start write byte
                    with open(path, 'wb') as f:
                        while length:
                            chunk = min(length, MAX_TRANSFER)
                            data = clientfile.read(chunk)
                            if not data:
                                flag = False
                                break

                            f.write(data)
                            length -= len(data)
                        else:
                            continue
                except:
                    flag = False

        return relpath if not flag else None

    def send_item(self, local_paths, remote_path):
        if not self.start_transfer(remote_path):
            self.transfer_result = "Cannot start transfering"
            return

        assert self.transfer_send is not None

        self.transfer_receive, _ = self.transfer_send.accept()
        print("Connected")

        with self.transfer_receive:
            for local_path in local_paths:
                root, file = os.path.split(local_path)
                if os.path.isdir(local_path):
                    self.send_folder(local_path, file)
                else:
                    self.send_file(root, file, '')

        self.end_transfer()

    def send_folder(self, path, rel):
        for root, dirs, files in os.walk(path):
            for dir in dirs:
                dirpath = os.path.join(root, dir)
                relpath = os.path.join(rel, dir)
                if not self.send_folder(dirpath, relpath):
                    return False

            for file in files:
                if not self.send_file(root, file, rel):
                    return False
            break
        return True

    def send_file(self, root, file, rel):
        filename = os.path.join(root, file)
        relpath = os.path.join(rel, file)
        size = os.path.getsize(filename)
        flag = True

        with open(filename, 'rb') as f:
            try:
                self.transfer_receive.sendall(relpath.encode() + b'\n')
                self.transfer_receive.sendall(f'{size}'.encode() + b'\n')

                s = self.receive_obj()

                if s[0] == "NO":
                    return flag

                sent = 0
                while True:
                    data = f.read(MAX_TRANSFER)
                    if not data:
                        break

                    self.transfer_receive.sendall(data)
                    sent += len(data)

            except:
                self.transfer_result = 'Cannot transfer {}'.format(relpath)
                flag = False

        return flag

    def close(self):
        try:
            self.client.shutdown(socket.SHUT_RDWR)
            self.client.close()
            super(ServerSocket, self).close()

        except:
            pass
