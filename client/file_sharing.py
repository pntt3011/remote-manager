from tkinter import ttk
import tkinter as tk
from RemoteFrame import RemoteFrame
from LocalFrame import LocalFrame
import os
class FileSharing:
    def __init__(self, parent, conn):
        self.parent = parent
        self.connection = conn
        self.sharing = tk.IntVar()
        self.share_button = ttk.Checkbutton(
            self.parent, text='Start file sharing', style='Toolbutton',
            variable=self.sharing, command=self.handle_share_button,
        )
        self.file_frame = None
        self.remote_frame = None
        self.local_frame = None
        self.file_sharing_icon = tk.PhotoImage(
            file=os.path.dirname(os.path.realpath(__file__)) + './res/file_sharing_icon.png'
        )
        self.stop_icon = tk.PhotoImage(
            file=os.path.dirname(os.path.realpath(__file__)) + './res/stop_icon.png'
        )
        self.set_stop_state_share()
    
    def handle_share_button(self):
        if self.sharing.get():
            self.set_start_state_share()
            
            if self.file_frame is None:
                self.file_frame = tk.Toplevel(self.parent)
                self.file_frame.iconbitmap(
                    os.path.dirname(os.path.realpath(__file__)) + './res/app_icon.ico'
                )
                self.file_frame.protocol("WM_DELETE_WINDOW", self.handle_quit_sharing)
                self.file_frame.title('File sharing')
                self.clipboard = [None] * 2

                self.file_frame.grid_rowconfigure(0, weight=1)
                self.file_frame.grid_columnconfigure(0, weight=1)
                self.file_frame.grid_columnconfigure(1, weight=1)

                self.local_frame = LocalFrame(self, self.file_frame, self.clipboard)
                self.local_frame.grid(row=0, column=0, padx=10, sticky="nsew")

                self.remote_frame = RemoteFrame(self, self.file_frame, self.clipboard)
                self.remote_frame.grid(row=0, column=1, padx=10, sticky="nsew")
                self.remote_frame.open_path()
    
            else:
                self.file_frame.deiconify()
            
            self.file_frame.state('zoomed')
            self.new_state = 'normal'
            self.file_frame.bind('<Configure>', self.handle_resize)

        else:
            self.set_stop_state_share()
            self.file_frame.withdraw()

    def set_start_state_share(self):
        self.share_button.configure(text='Stop file sharing',
                                    image=self.stop_icon,
                                    compound=tk.LEFT)
        self.sharing.set(True)

    def set_stop_state_share(self):
        self.share_button.configure(text='Start file sharing',
                                    image=self.file_sharing_icon,
                                    compound=tk.LEFT)
        self.sharing.set(False)

    def handle_resize(self, event):
        self.old_state = self.new_state # assign the old state value
        self.new_state = self.file_frame.state() # get the new state value
        if self.new_state == 'normal' and self.old_state == 'zoomed':
            self.file_frame.wm_geometry('960x540')

    def handle_quit_sharing(self):
        self.sharing.set(False)
        self.handle_share_button()

    def handle_lost_connection(self):
        self.set_stop_state_share()
        if self.file_frame is not None:
            self.file_frame.destroy()
            self.file_frame = None