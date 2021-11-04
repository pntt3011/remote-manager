from tkinter import ttk 
import tkinter as tk

class NetworkInfo:
    def __init__(self, parent, conn):
        self.parent = parent
        self.conn = conn
        self.info_frame = ttk.LabelFrame(self.parent, text='MAC address', padding=(5, 5))
        self.scrollbar = ttk.Scrollbar(self.info_frame)
        self.list = ttk.Treeview(
            self.info_frame, selectmode='browse', yscrollcommand=self.scrollbar.set,
        )
        self.scrollbar.config(command=self.list.yview)
        column = ('0', '1', '2', '3')
        self.list['columns'] = column
        self.list['show'] = 'headings'
        self.list.column('0', width=200, stretch=False)
        self.list.column('1', width=130, stretch=False)
        self.list.column('2', width=120, stretch=False)
        self.list.column('3', width=120, stretch=False)
        self.list.heading('0', text='Local area network', anchor=tk.W)
        self.list.heading('1', text='MAC address', anchor=tk.W)
        self.list.heading('2', text='IPv4', anchor=tk.W)
        self.list.heading('3', text='Subnet mask', anchor=tk.W)

        
    def get_MAC(self):
        if not self.conn.client.send_obj('MAC_ADDRESS'):
            return
        mac_address_items = self.conn.client.receive_obj()
        self.list.delete(*self.list.get_children())
        idx = 0
        for item in mac_address_items:
            self.list.insert(
                parent='', index=idx, iid=idx, text='', values=item
            )
            idx += 1

    def setup_UI(self):
        self.info_frame.pack(fill='both', expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.list.pack(fill='both', expand=True)

    def handle_lost_connection(self):
        self.list.delete(*self.list.get_children())

