from enum import Flag
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk, Image
from LocalFrame import LocalFrame
from RemoteFrame import RemoteFrame
from screen_sharing import ScreenSharing
from my_client import Client
from connection import Connection
from process_control import ProcessControl
from socket import socket, AF_INET, SOCK_STREAM
from BaseSocket import BaseSocket
import os
from ctypes import windll
import sys
from ttkbootstrap import Style

class ClientUI(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        self.root = parent
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        self.columnconfigure(index=0, weight=1)
        self.rowconfigure(index=0, weight=1)
        self.rowconfigure(index=1, weight=1000)
        self.setup_widgets()

    def setup_widgets(self):
        self.setup_connection_UI()

        # Widgets frame
        self.widgets_frame = ttk.Frame(self)
        self.widgets_frame.grid(row=1, column=0, sticky='nsew')
        self.notebook = ttk.Notebook(self.widgets_frame)
        self.notebook.pack(fill='both', expand=True)

        # Process control tab
        self.process_control_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.process_control_tab, text='Process control')
        self.process_control = ProcessControl(self.connection, self.process_control_tab)
        self.process_control.setup_UI()
        
        # Screen sharing tab
        self.screen_sharing_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.screen_sharing_tab, text='Screen capturing')
        self.screen_sharing = ScreenSharing(
            self.connection, self.screen_sharing_tab, self
        )
        self.screen_sharing.setup_UI()

        # Application control tab
        self.app_control_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.app_control_tab, text='Application control')

        # Share files tab
        self.share_files_tab = ttk.Frame(self.notebook)
        self.share_files_icon = ImageTk.PhotoImage(Image.open(
            os.path.dirname(os.path.realpath(__file__)) +
            '/res/share_files_icon.png'
        ))
        self.notebook.add(
            self.share_files_tab, text='Share files', image=self.share_files_icon, compound=tk.TOP
        )
        self.setup_share_files_tab()

        self.set_state_widgets('disabled')

    def set_state_widgets(self, state):
        for i in range(0, self.notebook.index('end')):
            self.notebook.tab(i, state=state)

    def setup_connection_UI(self):
        self.connection_frame = ttk.LabelFrame(self, text='Connection')
        self.connection_frame.grid(
            row=0, column=0, padx=(5, 5), pady=(5, 5), sticky='nsew'
        )
        self.connection_frame.columnconfigure(index=0, weight=3)
        self.connection_frame.columnconfigure(index=1, weight=1)
        self.connection_frame.columnconfigure(index=2, weight=50)
        self.connection_frame.rowconfigure(index=0, weight=1)
        self.connection = Connection(
            self.connection_frame, self)
        self.connection.ip_entry.grid(
            row=0, column=0, padx=(5, 5), pady=(5, 5), sticky="nsew"
        )
        self.connection.connect_button.grid(
            row=0, column=1, padx=(5, 5), pady=(5, 5), sticky="nsew"
        )
        # self.connection_frame.focus_set()

    def handle_failed_connection(self):
        messagebox.showerror(message="Can't connect to server.")

    def handle_accepted_connection(self):
        self.server_ip = self.connection.ip_entry.get()
        messagebox.showinfo(message='Successfully connect to server.')
        self.set_state_widgets('normal')
        self.remote_frame.open_path()

    def handle_lost_connection(self):
        print('Lost connection')
        self.connection.close()
        self.connection.client.set_root_window(self.root)
        self.set_state_widgets('disabled')
        messagebox.showerror(
            message='Connection to server lost. Please try to connect again.'
        )

    def setup_share_files_tab(self):
        self.connection.client.set_root_window(self.root)

        self.share_files_tab.grid_rowconfigure(0, weight=1)
        self.share_files_tab.grid_columnconfigure(0, weight=1)
        self.share_files_tab.grid_columnconfigure(1, weight=1)

        self.clipboard = [None] * 2

        self.local_frame = LocalFrame(self, self.clipboard)
        self.local_frame.grid(row=0, column=0, padx=10, sticky="nsew")

        self.remote_frame = RemoteFrame(self, self.clipboard)
        self.remote_frame.grid(row=0, column=1, padx=10, sticky="nsew")

    def destroy(self):
        try:
            if self.screen_sharing.sender is not None:
                self.screen_sharing.sender.stop_server()
                self.screen_sharing.sender = None

            self.connection.close()
        except Exception as e:
            print(e)
        super().destroy()


def is_admin():
    try:
        return windll.shell32.IsUserAnAdmin()
    except:
        return False


if __name__ == '__main__':

    if True:  # is_admin():
        root = tk.Tk()
        # root.geometry('500x400')
        # root.resizable(False, False)
        root.state('zoomed')
        root.title('Client')

        # Set the theme
        # root.tk.call("source", os.path.dirname(
        #     os.path.realpath(__file__)) + "/sun-valley.tcl")
        # root.tk.call("set_theme", "light")
        style = Style(theme='minty')
        root = style.master

        client_UI = ClientUI(root)
        client_UI.pack(fill="both", expand=True)

        # Set a minsize for the window, and place it in the middle
        root.update()
        root.minsize(root.winfo_width(), root.winfo_height())
        x_cordinate = int((root.winfo_screenwidth() / 2) -
                          (root.winfo_width() / 2))
        y_cordinate = int((root.winfo_screenheight() / 2) -
                          (root.winfo_height() / 2))
        root.geometry("+{}+{}".format(x_cordinate, y_cordinate))

        root.mainloop()

    else:
        windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
