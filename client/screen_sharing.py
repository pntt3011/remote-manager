from tkinter import messagebox
from tkinter.messagebox import NO
from typing import Text

from PIL import ImageTk
from streaming_server import StreamingServer
from my_client import Client
from tkinter import font, ttk
import time
import tkinter as tk
from ttkbootstrap import Style

FPS = 30

class ScreenSharing:
    def __init__(self, conn, parent, UI_control):
        self.conn = conn
        self.parent = parent
        self.UI_control = UI_control
        self.screen_frame = None
        
        self.running = tk.IntVar(self.parent)
        self.share_button = ttk.Checkbutton(
            self.parent, text='Start screen capturing', style='Toolbutton',
            variable=self.running, command=self.handle_share_button,
        )

        self.controlling  = tk.IntVar(self.parent)
        self.control_button = ttk.Checkbutton(
            self.parent, text='Start controlling', style='Toolbutton',
            variable=self.controlling, command=self.handle_control_button,
        )

        self.control_flag = False
        self.sender = None
        self.x_res = None
        self.y_res = None
        self.clock = time.time()

    def handle_control_button(self):
        if self.controlling.get():
            if not self.running.get():
                messagebox.showerror(message='Please start screen capturing first.')
                self.controlling.set(False)
            else:
                self.control_button_click()
        else:
            self.control_button_click()

    def setup_screen_frame(self):
        self.screen_frame = tk.Toplevel(self.parent)
        self.screen_frame.protocol("WM_DELETE_WINDOW", self.handle_quit_screen)
        self.screen_frame.title('Screen')
        self.picture = ttk.Label(self.screen_frame, anchor=tk.CENTER)
        self.picture.pack(fill='both', expand=True)
        self.screen_frame.bind('<Configure>', self.handle_resize)

    def handle_share_button(self):
        if self.running.get():
            self.share_button.configure(text='Stop screen capturing')
            
            if self.screen_frame is None:
                self.setup_screen_frame()
                self.setup_remote_control()
            else:
                self.screen_frame.deiconify()
            
            self.screen_frame.state('zoomed')
            self.new_state = 'normal'
            self.start_button_click()

        else:
            if self.controlling.get():
                self.controlling.set(False)
                self.handle_control_button()
            self.share_button.configure(text='Start screen capturing')
            self.screen_frame.withdraw()
            self.stop_button_click()

    def handle_resize(self, event):
        self.old_state = self.new_state # assign the old state value
        self.new_state = self.screen_frame.state() # get the new state value
        if self.new_state == 'normal' and self.old_state == 'zoomed':
            self.screen_frame.wm_geometry('960x540')
        self.set_res()
        

    def set_res(self):
        self.picture.update()
        self.x_orig = self.picture.winfo_width()
        self.y_orig = self.picture.winfo_height()
        self.x_res = min(self.x_orig, int(16/9 * self.y_orig))
        self.y_res = min(self.y_orig, int(9/16 * self.x_orig))
        self.x_offset = (self.x_orig - self.x_res) / 2
        self.y_offset = (self.y_orig - self.y_res) / 2
        # print(self.x_res, 'x', self.y_res)
        if not self.conn.client.send_obj("SET_RESOLUTION"):
            return False
        if not self.conn.client.send_obj([self.x_res, self.y_res]):
            return False
        return True

    def handle_quit_screen(self):
        self.running.set(False)
        self.handle_share_button()

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
            self.conn.client_io.send_obj(["KEY_PRESS", event.keysym])

    def keyup(self, event):
        if self.control_flag and self.sender is not None:
            self.conn.client_io.send_obj(["KEY_RELEASE", event.keysym])

    def mousedown(self, m):
        if self.control_flag and self.sender is not None:
            self.conn.client_io.send_obj(["MOUSE_DOWN", m])

    def mouseup(self, m):
        if self.control_flag and self.sender is not None:
            self.conn.client_io.send_obj(["MOUSE_UP", m])

    def motion(self, event):
        if self.control_flag and self.sender is not None:
            if FPS * (time.time() - self.clock) >= 1:
                x = (event.x - self.x_offset) / self.x_res
                y = (event.y - self.y_offset) / self.y_res

                if x >= 0 and x <= 1 and y >= 0 and y <= 1:
                    self.conn.client_io.send_obj(["MOUSE_MOVE", [repr(x), repr(y)]])
                    self.clock = time.time()

    def start_button_click(self):
        if not self.set_res():
            return

        if self.sender is None:
            if not self.conn.client.send_obj("START_CAPTURE"):
                return
            self.sender = StreamingServer(
                self.UI_control, '', 9696, self.picture
            )
        self.sender.start_server()

    def stop_button_click(self):
        if not self.conn.client.send_obj("STOP_CAPTURE"):
            return
        if self.sender is not None:
            self.sender.stop_server()
            self.sender = None

    def handle_lost_connection(self):
        self.running.set(False)
        self.share_button.configure(text='Start screen capturing')
        self.controlling.set(False)
        self.share_button.configure(text='Start screen controlling')
        if self.screen_frame is not None:
            self.screen_frame.destroy()
            self.screen_frame = None

        if self.sender is not None:
            self.sender.stop_server()
            self.sender = None
        
        # self.UI_control.handle_lost_connection()

    def control_button_click(self):
        self.control_flag = not self.control_flag
        if str(self.control_button.cget("text")) == "Start controlling" and self.sender is not None:
            self.control_button.configure(text="Stop controlling")
            self.picture.focus_set()
        else:
            self.control_button.configure(text="Start controlling")

