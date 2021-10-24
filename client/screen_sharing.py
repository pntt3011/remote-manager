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
                                       text='Start capturing',
                                       style='Accent.TButton',
                                       command=self.start_button_click,)
        self.stop_button = ttk.Button(parent,
                                      text='Stop capturing',
                                      style='Accent.TButton',
                                      command=self.stop_button_click,)
        self.picture = ttk.Label(self.screen_frame)
        self.sender = None
        self.x_res = None
        self.y_res = None

        self.setup_remote_control()

    def setup_remote_control(self):
        self.picture.bind("<KeyPress>", self.keydown)
        self.picture.bind("<KeyRelease>", self.keyup)

        self.picture.bind("<ButtonPress-1>", lambda e: self.mousedown("left"))
        self.picture.bind("<ButtonRelease-1>", lambda e: self.mouseup("left"))

        self.picture.bind("<ButtonPress-3>", lambda e: self.mousedown("right"))
        self.picture.bind("<ButtonRelease-3>", lambda e: self.mouseup("right"))

        self.picture.bind("<Motion>", self.motion)

    def keydown(self, event):
        if self.sender is not None:
            self.client.send_obj(["KEY_PRESS", event.keysym])

    def keyup(self, event):
        if self.sender is not None:
            self.client.send_obj(["KEY_RELEASE", event.keysym])

    def mousedown(self, m):
        if self.sender is not None:
            self.client.send_obj(["MOUSE_DOWN", m])

    def mouseup(self, m):
        if self.sender is not None:
            self.client.send_obj(["MOUSE_UP", m])

    def motion(self, event):
        if self.sender is not None:
            x = repr(min(event.x / self.x_res, 1.))
            y = repr(min(event.y / self.y_res, 1.))
            self.client.send_obj(["MOUSE_MOVE", [x, y]])

    def start_button_click(self):
        self.picture.focus_set()

        if not self.client.send_obj("SET_RESOLUTION"):
            return
        self.x_res = self.picture.winfo_width()
        self.y_res = self.picture.winfo_height()
        self.x_res, self.y_res = min(
            self.x_res, 16/9 * self.y_res), min(self.y_res, 9/16 * self.x_res)
        if not self.client.send_obj([self.x_res, self.y_res]):
            return

        if self.sender is None:
            if not self.client.send_obj("START_CAPTURE"):
                return
            self.sender = StreamingServer(
                self.UI_control, '', 9696, self.picture
            )
        self.sender.start_server()

    def stop_button_click(self):
        if not self.client.send_obj("STOP_CAPTURE"):
            return
        if self.sender is not None:
            self.sender.stop_server()
            self.sender = None
