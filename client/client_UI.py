from tkinter import ttk, messagebox
from typing import Counter
from win32process import SetProcessAffinityMask
from power_control import PowerControl
from screen_sharing import ScreenSharing
from file_sharing import FileSharing
from connection import Connection
from process_control import ProcessControl
from key_hooker import KeyHooker
from network_info import NetworkInfo
from registry_editor import RegistryEditor
from application_control import ApplicationControl
import tkinter as tk
import os

class ClientUI(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        self.root = parent
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        self.columnconfigure(index=0, weight=1)
        self.rowconfigure(index=0, weight=1)
        self.rowconfigure(index=1, weight=1000)
        self.setup_widgets()

    def setup_widgets(self):
        # Widgets frame
        self.widgets_frame = ttk.Frame(self)
        self.widgets_frame.grid(row=1, column=0, sticky='nsew')
        self.notebook = ttk.Notebook(self.widgets_frame)
        self.notebook.pack(fill='both', expand=True)

        # Connection tab
        self.connection_tab = ttk.Frame(self.notebook)
        self.connect_icon = tk.PhotoImage(
            file=os.path.dirname(os.path.realpath(__file__)) + './res/connect_icon.png'
        )
        self.notebook.add(
            self.connection_tab, text='Connect', image=self.connect_icon, compound=tk.TOP)
        self.connection = Connection(self.connection_tab, self)
        self.connection.setup_UI()

        # Process control tab
        self.process_control_tab = ttk.Frame(self.notebook)
        self.process_icon = tk.PhotoImage(
            file=os.path.dirname(os.path.realpath(__file__)) + './res/process_icon.png'
        )
        self.notebook.add(self.process_control_tab, text='Process',
                          image=self.process_icon, compound=tk.TOP)
        self.process_control = ProcessControl(self.connection, self.process_control_tab)
        self.process_control.setup_UI()
        
        # Application control tab
        self.app_control_tab = ttk.Frame(self.notebook)
        self.application_icon = tk.PhotoImage(
            file=os.path.dirname(os.path.realpath(__file__)) + './res/application_icon.png'
        )
        self.notebook.add(self.app_control_tab, text='Application',
                          image=self.application_icon, compound=tk.TOP)
        self.app_control = ApplicationControl(self.connection, self.app_control_tab)
        self.app_control.setup_UI()
        
        # Sharing tab
        self.sharing_tab = ttk.Frame(self.notebook)
        self.share_icon = tk.PhotoImage(
            file=os.path.dirname(os.path.realpath(__file__)) + './res/share_icon.png'
        )
        self.notebook.add(self.sharing_tab, text='Share', image=self.share_icon, compound=tk.TOP)
        self.setup_sharing_tab()

        # Keyboard control tab
        self.keyboard_control_tab = ttk.Frame(self.notebook)
        self.keyboard_icon = tk.PhotoImage(
            file=os.path.dirname(os.path.realpath(__file__)) + './res/keyboard_icon.png'
        )
        self.notebook.add(self.keyboard_control_tab, text='Keyboard',
                          image=self.keyboard_icon, compound=tk.TOP)
        self.key_hooker = KeyHooker(self.keyboard_control_tab, self.connection)
        self.key_hooker.setup_UI()

        # MAC collecting tab
        self.network_tab = ttk.Frame(self.notebook)
        self.mac_address_icon = tk.PhotoImage(
            file=os.path.dirname(os.path.realpath(__file__)) + './res/mac_address_icon.png'
        )
        self.notebook.add(self.network_tab, text='Network',
                          image=self.mac_address_icon, compound=tk.TOP)
        self.network_info = NetworkInfo(self.network_tab, self.connection)

        # Power control tab
        self.power_tab = ttk.Frame(self.notebook)
        self.power_icon = tk.PhotoImage(
            file=os.path.dirname(os.path.realpath(__file__)) + './res/power_icon.png'
        )
        self.notebook.add(self.power_tab, text='Power', image=self.power_icon, compound=tk.TOP)
        self.power_control = PowerControl(self.power_tab, self.connection)
        self.power_control.setup_UI()

        # Registry editor tab
        self.registry_editor_tab = ttk.Frame(self.notebook)
        self.registry_editor_icon = tk.PhotoImage(
            file=os.path.dirname(os.path.realpath(__file__)) + './res/registry_editor_icon.png'
        )
        self.notebook.add(self.registry_editor_tab, text='Registry',
                          image=self.registry_editor_icon, compound=tk.TOP)
        self.registry_editor = RegistryEditor(self.registry_editor_tab, self.connection)
        self.registry_editor.setup_UI()

        self.widgets = [self.connection, self.process_control, self.app_control,
                        self.key_hooker, self.network_info, self.file_sharing,
                        self.screen_sharing, self.registry_editor]
        self.network_info.setup_UI()

        self.set_state_widgets('disabled')

    def set_state_widgets(self, state):
        for i in range(1, self.notebook.index('end')):
            self.notebook.tab(i, state=state)

    def handle_failed_connection(self):
        messagebox.showerror(message="Can't connect to server.")

    def handle_accepted_connection(self):
        self.server_ip = self.connection.ip_entry.get()
        messagebox.showinfo(message='Successfully connect to server.')
        self.connection.client.set_root_window(self.root)
        self.connection.off_button()
        self.set_state_widgets('normal')

    def handle_lost_connection(self):
        print('Lost connection')
        
        # Call handle function of widgets
        for widget in self.widgets:
            widget.handle_lost_connection()
        
        self.connection.close()
        self.set_state_widgets('disabled')
        self.connection.on_button()
        messagebox.showerror(
            message='Connection to server lost. Please try to connect again.'
        )

    def setup_sharing_tab(self):
        self.screen_sharing = ScreenSharing(
            self.connection, self.sharing_tab, self
        )
        self.file_sharing = FileSharing(self.sharing_tab, self.connection)

        self.sharing_tab.rowconfigure(0, weight=5)
        self.sharing_tab.rowconfigure(1, weight=1)
        self.sharing_tab.rowconfigure(2, weight=1)
        self.sharing_tab.rowconfigure(3, weight=1)
        self.sharing_tab.rowconfigure(4, weight=25)
        self.sharing_tab.columnconfigure(0, weight=3)
        self.sharing_tab.columnconfigure(1, weight=1)
        self.sharing_tab.columnconfigure(2, weight=3)
        self.screen_sharing.share_button.grid(
            row=1, column=1, padx=(5, 5), pady=(5, 5), sticky="nsew"
        )
        self.screen_sharing.control_button.grid(
            row=2, column=1, padx=(5, 5), pady=(5, 5), sticky="nsew"
        )
        self.file_sharing.share_button.grid(
            row=3, column=1, padx=(5, 5), pady=(5, 5), sticky="nsew"
        )

    def destroy(self):
        try:
            if self.screen_sharing.sender is not None:
                self.screen_sharing.sender.stop_server()
                self.screen_sharing.sender = None

            self.connection.close()
        except Exception as e:
            print(e)
        super().destroy()



