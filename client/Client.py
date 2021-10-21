from my_client import Client
import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style
from tkinter import messagebox
from LocalFrame import LocalFrame
from RemoteFrame import RemoteFrame
from ctypes import windll

import sys
import socket


class App:
    def __init__(self):
        if self.is_admin():
            self.client = Client(socket.AF_INET, socket.SOCK_STREAM)
            self.add_root()
            self.add_login()
            self.add_main_frame()
            self.root.mainloop()

        else:
            windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )

    def is_admin(self):
        try:
            return windll.shell32.IsUserAnAdmin()
        except:
            return False

    def add_root(self):
        style = Style(theme='cosmo')
        self.root = style.master

        # self.root.tk.call("source", "sun-valley.tcl")
        # self.root.tk.call("set_theme", "light")

        self.root.resizable(False, False)
        self.root.geometry("1280x720+10+10")
        self.client.set_root_window(self.root)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=20)
        self.root.grid_columnconfigure(0, weight=1)

    def add_login(self):
        self.button_login = ttk.Button(
            self.root, text="connect", command=self.connect)
        self.button_login.grid(row=0, column=0)

    def connect(self):
        try:
            self.client.connect(("192.168.1.227", 8080))
            self.remote_frame.reset_path()

        except:
            messagebox.showerror("Error", "Cannot connect to client.")
            return

    def add_main_frame(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid(row=1, column=0, sticky="nsew")

        self.local_frame = LocalFrame(self)
        self.local_frame.grid(row=0, column=0, padx=10, sticky="nsew")

        self.remote_frame = RemoteFrame(self)
        self.remote_frame.grid(row=0, column=1, padx=10, sticky="nsew")


if __name__ == "__main__":
    App()
