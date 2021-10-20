from tkinter.messagebox import NO
from streaming_server import StreamingServer
from my_client import Client
from tkinter import ttk
import time
class ScreenSharing:
    def __init__(self, client, parent, screen_frame, UI_control):
        self.client = client
        self.parent = parent
        self.screen_frame = screen_frame
        self.UI_control = UI_control
        self.mystyle = ttk.Style(self.parent)
        self.start_button = ttk.Button(parent,
                                        text='Start sharing',
                                        style='Accent.TButton',
                                        command=self.start_button_click,)
        self.stop_button = ttk.Button(parent,
                                        text='Stop sharing',
                                        style='Accent.TButton',
                                        command=self.stop_button_click,)
        self.picture = ttk.Label(self.screen_frame)
        self.sender = None

    def start_button_click(self):
        self.client.send_signal("SET_RESOLUTION")
        x_res = self.picture.winfo_width()
        y_res = self.picture.winfo_height()
        x_res, y_res = min(x_res, 16/9 * y_res), min(y_res, 9/16 * x_res)
        self.client.send_obj([x_res, y_res])
        # log = self.client.receive_signal()
        # print(log)
        if self.sender is None:
            self.client.send_signal("START_CAPTURE")
            self.sender = StreamingServer(
                self.UI_control, self.UI_control.server_ip, 9999, self.picture
            )
        self.sender.start_server()

    def stop_button_click(self):
        self.client.send_signal("STOP_CAPTURE")
        if self.sender is not None:
            self.sender.stop_server()
            self.sender = None