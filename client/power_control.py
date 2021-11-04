import tkinter as tk
from tkinter import ttk
import os
from path_finding import resource_path

class PowerControl:
    def __init__(self, parent, conn):
        self.parent = parent
        self.conn = conn
        self.shutdown_icon = tk.PhotoImage(file=resource_path('res/power_icon.png'))
        self.shutdown_button = ttk.Button(
            self.parent, text='Shut down', command=self.handle_shutdown_button,
            image=self.shutdown_icon, compound=tk.LEFT
        )
        self.logout_icon = tk.PhotoImage(file=resource_path('res/logout_icon.png'))
        self.logout_button = ttk.Button(
            self.parent, text='Log out', command=self.handle_logout_button,
            image=self.logout_icon, compound=tk.LEFT
        )

    def handle_shutdown_button(self):
        self.conn.client.send_obj('SHUTDOWN')

    def handle_logout_button(self):
        self.conn.client.send_obj('LOGOUT')

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
        self.shutdown_button.grid(
            row=1, column=1, padx=(5, 5), pady=(5, 5), sticky="nsew"
        )
        self.logout_button.grid(
            row=2, column=1, padx=(5, 5), pady=(5, 5), sticky="nsew"
        )

    def handle_lost_connection(self):
        pass