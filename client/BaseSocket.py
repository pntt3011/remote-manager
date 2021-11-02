from struct import pack, unpack
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
import socket
import pickle
import os

MAX_LEN = 8192
MAX_TRANSFER = 1024 * 256
HEADER_SIZE = 8


class BaseSocket(socket.socket):
    def __init__(self, *args, **kwargs):
        super(BaseSocket, self).__init__(*args, **kwargs)
        self.client = None
        self.client_addr = None
        self.transfer_send = None
        self.transfer_receive = None
        self.transfer_result = None
        self.monitor_window = None
        self.display = False

    def set_root_window(self, tk):
        self.root_tk = tk

    def connect(self, address):
        super(BaseSocket, self).connect(address)
        self.client = self
        self.client_addr = address[0]
    
    def close(self):
        super().close()

    def accept(self):
        self.client, addr = super(BaseSocket, self).accept()
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
        finally:
            print("End transfer")
            self.transfer_send = None

    def receive_item(self, root, display_progress=False):
        flag = True
        relpath = None

        self.display = display_progress
        self.start_monitor("Receiving")
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

                    if self.display:
                        self.info.set(f"Receiving {relpath}")

                    path = os.path.join(root, relpath)

                    # Check if path exists
                    if os.path.exists(path):
                        answer = messagebox.askyesnocancel(
                            title='Duplicate File', message=f'{path} existed. Do you want to overwrite it? \nPress No to make a copy, Cancel to skip this file.')
                        
                        if answer:
                            self.send_obj(['YES'])
                        elif answer is None:
                            self.send_obj(['NO'])
                        else:
                            while True:
                                dir, name = os.path.split(path)
                                name = "Copy of " + name
                                path = os.path.join(dir, name)
                                if not os.path.exists(path):
                                    break
                            self.send_obj(['YES'])

                    else:
                        self.send_obj(["YES"])

                    print(f"Receiving {path}")
                    os.makedirs(os.path.dirname(path), exist_ok=True)

                    # Start write byte
                    size = length
                    receive = 0
                    with open(path, 'wb') as f:
                        while length:
                            chunk = min(length, MAX_TRANSFER)
                            data = clientfile.read(chunk)
                            if not data:
                                flag = False
                                break

                            f.write(data)
                            length -= len(data)
                            receive += len(data)
                            if self.display:
                                self.progress_bar['value'] = int(
                                    receive / size * 100)
                                self.monitor_window.update()

                        else:
                            continue
                except:
                    flag = False

        self.end_monitor()
        return relpath if not flag else None

    def send_item(self, local_paths, remote_path, display_progress=False):
        if not self.start_transfer(remote_path):
            self.transfer_result = "Cannot start transfering"
            return

        assert self.transfer_send is not None
        self.display = display_progress
        self.start_monitor("Sending")

        self.transfer_receive, _ = self.transfer_send.accept()
        print("Connected")

        with self.transfer_receive:
            for local_path in local_paths:
                root, file = os.path.split(local_path)
                if os.path.isdir(local_path):
                    self.send_folder(local_path, file)
                else:
                    self.send_file(root, file, '')

        self.end_monitor()
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

        if self.display:
            self.info.set(f"Sending {filename}")

        with open(filename, 'rb') as f:
            try:
                self.transfer_receive.sendall(relpath.encode() + b'\n')
                self.transfer_receive.sendall(f'{size}'.encode() + b'\n')

                dup_flag = True
                s = self.receive_obj()

                if s[0] == "DUPLICATE":
                    answer = messagebox.askyesnocancel(
                        title='Duplicate File', message=f'{s[1]} existed. Do you want to overwrite it? \nPress No to make a copy, Cancel to skip this file.')

                    if answer:
                        self.send_obj(['OVERWRITE'])
                    elif answer is None:
                        self.send_obj(['NO'])
                        dup_flag = False
                    else:
                        self.send_obj(['RENAME'])

                if dup_flag:
                    sent = 0
                    while True:
                        data = f.read(MAX_TRANSFER)
                        if not data:
                            break

                        self.transfer_receive.sendall(data)
                        sent += len(data)
                        if self.display:
                            self.progress_bar['value'] = int(sent / size * 100)
                            self.monitor_window.update()

            except:
                self.transfer_result = 'Cannot transfer {}'.format(relpath)
                flag = False

        return flag

    def close(self):
        assert self.client != None

        try:
            self.client.shutdown(socket.SHUT_RDWR)
            self.client.close()
            super(BaseSocket, self).close()

        except:
            pass

    def start_monitor(self, title):
        if self.display:
            self.monitor_window = tk.Toplevel(self.root_tk)
            self.monitor_window.title = title
            self.monitor_window.resizable(0, 0)
            self.root_tk.wm_attributes("-disabled", True)

            window_height = 60
            window_width = 420

            screen_width = self.monitor_window.winfo_screenwidth()
            screen_height = self.monitor_window.winfo_screenheight()

            x_cordinate = int((screen_width/2) - (window_width/2))
            y_cordinate = int((screen_height/2) - (window_height/2))

            self.monitor_window.geometry(
                "{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

            self.info = tk.StringVar(
                self.monitor_window, value="Waiting for connect....")

            label = ttk.Label(self.monitor_window, textvariable=self.info)
            label.pack()

            self.progress_bar = ttk.Progressbar(self.monitor_window, orient=tk.HORIZONTAL,
                                                length=400, mode='determinate')
            self.progress_bar.pack(expand=True, padx=10, pady=10)

            self.monitor_window.update()

    def end_monitor(self):
        self.display = False
        if self.monitor_window is not None:
            try:
                self.root_tk.wm_attributes("-disabled", False)
                self.monitor_window.destroy()

            finally:
                self.monitor_window = None
