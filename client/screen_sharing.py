from tkinter.messagebox import NO
from streaming_server import StreamingServer
from my_client import Client
from tkinter import ttk
import time


class ScreenSharing:
    def __init__(self, client, client_io, parent, screen_frame, UI_control):
        self.client = client
        self.client_io = client_io
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
        self.control_button = ttk.Button(parent,
                                         text='Start controlling',
                                         style='Accent.TButton',
                                         command=self.control_button_click,)
        self.picture = ttk.Label(self.screen_frame)
        self.control_flag = False
        self.sender = None
        self.x_res = None
        self.y_res = None
        self.clock = time.time()

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
        if self.control_flag and self.sender is not None:
            self.client_io.send_obj(["KEY_PRESS", event.keysym])

    def keyup(self, event):
        if self.control_flag and self.sender is not None:
            self.client_io.send_obj(["KEY_RELEASE", event.keysym])

    def mousedown(self, m):
        if self.control_flag and self.sender is not None:
            self.client_io.send_obj(["MOUSE_DOWN", m])

    def mouseup(self, m):
        if self.control_flag and self.sender is not None:
            self.client_io.send_obj(["MOUSE_UP", m])

    def motion(self, event):
        if self.control_flag and self.sender is not None:
            if 10 * (time.time() - self.clock) >= 1:
                x = repr(min(event.x / self.x_res, 1.))
                y = repr(min(event.y / self.y_res, 1.))
                self.client_io.send_obj(["MOUSE_MOVE", [x, y]])
                self.clock = time.time()

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

    def control_button_click(self):
        self.control_flag = not self.control_flag
        if str(self.control_button.cget("text")) == "Start controlling" and self.sender is not None:
            self.control_button.configure(text="Stop controlling")
        else:
            self.control_button.configure(text="Start controlling")
