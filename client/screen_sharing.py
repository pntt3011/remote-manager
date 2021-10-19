from streaming_server import StreamingServer
from my_client import Client
from tkinter import ttk

class ScreenSharing:
    def __init__(self, client, parent, UI_control):
        self.UI_control = UI_control
        self.client = client
        self.parent = parent
        self.mystyle = ttk.Style(self.parent)
        self.mystyle.configure('TButton', font=('Segoe Ui', 10))
        self.start_button = ttk.Button(parent,
                                        text='Start sharing',
                                        command=self.start_button_click,)
        self.stop_button = ttk.Button(parent,
                                        text='Stop sharing',
                                        command=self.stop_button_click,)
        self.picture = ttk.Label(self.parent)
        self.sender = None

    def start_button_click(self):
        self.client.send_signal("START_CAPTURE")
        self.sender = StreamingServer(self.UI_control.server_ip, 9999, self.picture)
        self.sender.start_server()

    def stop_button_click(self):
        self.client.send_signal("STOP_CAPTURE")
        self.sender.stop_server()
        self.sender = None