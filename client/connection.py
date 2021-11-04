from socket import AF_INET, SOCK_STREAM
from my_client import Client
from tkinter import font, ttk
from my_entry import MyEntry
from my_client import Client
from BaseSocket import BaseSocket
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
        self.connect_button.bind("<Return>", self.handle_enter)
        self.ip_entry.bind("<Return>", self.handle_enter)
        self.connect_button.focus()

    def handle_enter(self, _):
        self.connect_button_click()

    def connect_button_click(self):
        server_ip = self.ip_entry.get()
        print(server_ip)
        if server_ip == '':
            server_ip = 'localhost'
        try:
            self.client.connect(server_ip)
            self.client_io.connect((server_ip, IO_PORT))
            self.UI_control.handle_accepted_connection()
            return True
        except Exception as e:
            print(e)
            print(self.client.client)
            print(self.client_io.client)
            self.UI_control.handle_failed_connection()
            return False

    def close(self):
        self.client.close()
        self.client_io.close()
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
        pass

    def on_button(self):
        self.connect_button['state'] = 'normal'
        self.connect_button.configure(text='Connect')

    def off_button(self):
        self.connect_button['state'] = 'disabled'
        self.connect_button.configure(text='Connected')