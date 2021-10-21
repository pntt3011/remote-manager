import tkinter as tk
from tkinter import PhotoImage, ttk, messagebox
from PIL import ImageTk, Image
from matplotlib import image
from screen_sharing import ScreenSharing
from my_client import Client
from connection import Connection
from socket import socket, AF_INET, SOCK_STREAM
from ttkbootstrap import Style
import os


class ClientUI(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        self.client = Client(self, AF_INET, SOCK_STREAM)

        self.columnconfigure(index=0, weight=1)
        self.rowconfigure(index=0, weight=1)
        self.rowconfigure(index=1, weight=1000)
        self.setup_widgets()

    def setup_widgets(self):
        self.setup_connection_UI()

        self.widgets_frame = ttk.Frame(self)
        self.widgets_frame.grid(row=1, column=0, sticky='nsew')
        self.notebook = ttk.Notebook(self.widgets_frame)
        self.notebook.pack(fill='both', expand=True)

        self.control_tab = ttk.Frame(self.notebook)
        self.control_icon = ImageTk.PhotoImage(Image.open(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), 'res/control_icon.png')))
        self.notebook.add(
            self.control_tab, text='Control', image=self.control_icon, compound=tk.TOP
        )
        self.setup_control_tab()

        self.share_files_tab = ttk.Frame(self.notebook)
        self.share_files_icon = ImageTk.PhotoImage(Image.open(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), 'res/share_files_icon.png')))
        self.notebook.add(
            self.share_files_tab, text='Share files', image=self.share_files_icon, compound=tk.TOP
        )
        self.setup_share_files_tab()

        self.set_state_widgets('disabled')

    def set_state_widgets(self, state):
        for i in range(0, 2):
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
        self.connection = Connection(self.client, self.connection_frame, self)
        self.connection.ip_entry.grid(
            row=0, column=0, padx=(5, 5), pady=(5, 5), sticky="nsew"
        )
        self.connection.connect_button.grid(
            row=0, column=1, padx=(5, 5), pady=(5, 5), sticky="nsew"
        )

    def connect_failed_handle(self):
        messagebox.showerror(message="Can't connect to server!")
        self.client = None

    def connect_accepted_handle(self):
        self.server_ip = self.connection.ip_entry.get()
        messagebox.showinfo(message='Successfully connect to server!')
        self.set_state_widgets('normal')

    def lost_connection_handle(self):
        print('cacac')
        if self.client is not None:
            self.client.close()
            self.client = None
        self.set_state_widgets('disabled')
        messagebox.showerror(
            message='Connection to server lost! Please try to connect again.'
        )

    def setup_control_tab(self):
        self.notebook_control_style = ttk.Style(self.control_tab)
        self.notebook_control_style.configure(
            'lefttab.TNotebook', tabposition='wn')
        self.notebook_control = ttk.Notebook(
            self.control_tab, style='lefttab.TNotebook')
        self.notebook_control.pack(fill='both', expand=True)

        self.screen_sharing_tab = ttk.Frame(self.notebook_control)
        self.notebook_control.add(
            self.screen_sharing_tab, text='Screen sharing')
        self.setup_sharing_tab()

        # self.process_control_tab = ttk.Frame(self.notebook_control)
        # self.notebook_control.add(self.process_control_tab, text='Process control')

    def setup_sharing_tab(self):
        self.screen_sharing_tab.rowconfigure(index=0, weight=1)
        self.screen_sharing_tab.rowconfigure(index=1, weight=10000)
        self.screen_sharing_tab.columnconfigure(index=0, weight=1)
        self.screen_sharing_tab.columnconfigure(index=1, weight=1)
        self.screen_sharing_tab.columnconfigure(index=2, weight=100)

        self.screen_frame = ttk.LabelFrame(
            self.screen_sharing_tab, text='Screen', padding=(5, 5)
        )
        self.screen_frame.grid(
            row=1, column=0, columnspan=3, padx=(5, 70), pady=(5, 5), sticky="nsew"
        )
        self.screen_sharing = ScreenSharing(
            self.client, self.screen_sharing_tab, self.screen_frame, self
        )

        self.screen_sharing.start_button.grid(
            row=0, column=0, padx=(5, 5), pady=(5, 5), sticky="nsew"
        )
        self.screen_sharing.stop_button.grid(
            row=0, column=1, padx=(5, 5), pady=(5, 5), sticky="nsew"
        )

        self.screen_sharing.picture.pack(fill='both', expand=True)

    def setup_share_files_tab(self):
        # in Frame self.share_files_tab
        # Tung add here
        pass

    def destroy(self):
        try:
            if self.screen_sharing.sender is not None:
                self.screen_sharing.sender.stop_server()
                self.screen_sharing.sender = None

            if self.client is not None:
                self.client.close()
                self.client = None
        except Exception as e:
            print(e)
        super().destroy()


if __name__ == '__main__':
    style = Style('cosmo')
    root = style.master
    root.state('zoomed')
    root.title('Client')

    # Set the theme
    # root.tk.call("source", "sun-valley.tcl")
    # root.tk.call("set_theme", "light")
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
