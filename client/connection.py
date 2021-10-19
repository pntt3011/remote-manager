from typing import Sized
from my_client import Client
from tkinter import font, ttk

class Connection:
    def __init__(self, client, parent, UI_control):
        self.UI_control = UI_control
        self.client = client
        self.ip_entry = ttk.Entry(parent, justify='center', font=("-size", 13))
        self.connect_button = ttk.Button(parent,
                                        text='Connect',
                                        command=self.connect_button_click,)
        self.mystyle = ttk.Style(self.connect_button)
        self.mystyle.configure('TButton', font=('Segoe Ui', 13))

    def connect_button_click(self):
        server_ip = self.ip_entry.get();
        print(server_ip)
        try:
            self.client.connect(server_ip)
            self.UI_control.connect_accepted_handle()
            return True
        except:
            self.UI_control.connect_failed_handle()
            return False