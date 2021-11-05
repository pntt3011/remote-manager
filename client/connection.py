from socket import AF_INET, SOCK_STREAM
from tkinter.messagebox import showerror
from my_client import Client
from tkinter import font, ttk
from my_entry import MyEntry
from my_client import Client
from BaseSocket import BaseSocket
import tkinter as tk
import gc

IO_PORT = 5656


class Connection:
    def __init__(self, parent, UI_control):
        self.UI_control = UI_control
        self.client = Client(UI_control, AF_INET, SOCK_STREAM)
        self.client_io = BaseSocket(AF_INET, SOCK_STREAM)
        self.parent = parent
        self.ip_entry = MyEntry(
            self.parent, 'Enter host ip', justify='center', font=("Segoe Ui", 13),
        )
        self.connect_button = ttk.Button(parent,
                                         text='Connect',
                                         style='Accent.TButton',
                                         command=self.connect_button_click)
        self.connected = tk.BooleanVar(False)
        self.connect_button.bind("<Return>", self.handle_enter)
        self.ip_entry.bind("<Return>", self.handle_enter)
        self.connect_button.focus()

    def handle_enter(self, _):
        self.connect_button_click()

    def connect_button_click(self):
        if not self.connected.get():
            server_ip = self.ip_entry.get()
            print(server_ip)
            if server_ip == '':
                server_ip = 'localhost'
            try:
                self.client.connect(server_ip)
                self.client_io.connect((server_ip, IO_PORT))
                self.UI_control.handle_accepted_connection()
                self.set_connected_state()
            except Exception as e:
                print(e)
                print(self.client.client)
                print(self.client_io.client)
                self.UI_control.handle_failed_connection()
                self.set_disconnected_state()
        else:
            self.UI_control.handle_lost_connection(show_error=False)
            self.set_disconnected_state()

    def set_connected_state(self):
        self.connect_button.configure(text='Disconnect')
        self.connected.set(True)

    def set_disconnected_state(self):
        self.connect_button.configure(text='Connect')
        self.connected.set(False)

    def close(self):
        try:
            self.client.close()
            self.client_io.close()
        except:
            pass
        self.client = Client(self.UI_control, AF_INET, SOCK_STREAM)
        self.client_io = BaseSocket(AF_INET, SOCK_STREAM)
    
    def setup_UI(self):
        # Setup grid
        self.parent.columnconfigure(index=0, weight=2)
        self.parent.columnconfigure(index=1, weight=1)
        self.parent.columnconfigure(index=2, weight=2)
        self.parent.rowconfigure(index=0, weight=5)
        self.parent.rowconfigure(index=1, weight=1)
        self.parent.rowconfigure(index=2, weight=1)
        self.parent.rowconfigure(index=3, weight=20)

        # Put tkinter widgets into grid
        self.ip_entry.grid(
            row=1, column=1, padx=(5, 5), pady=(5, 5), sticky="nsew"
        )
        self.connect_button.grid(
            row=2, column=1, padx=(5, 5), pady=(5, 5), sticky="ns",
        )

    def handle_lost_connection(self):
        self.set_disconnected_state()