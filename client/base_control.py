from tkinter import StringVar, Toplevel, ttk
import tkinter as tk
from my_entry import MyEntry

class BaseControl:
    def __init__(self, client, parent):
        self.client = client
        self.parent=  parent
        self.run_frame = ttk.LabelFrame(
            self.parent, text='Run process', padding=(5, 5)
        )
        self.entry = MyEntry(self.run_frame, '', '', justify='center', font=("-size", 13))
        self.run_button = ttk.Button(
            self.run_frame, text='Start', style='Accent.TButton', command=self.run_button_click
        )
        self.kill_button = ttk.Button(
            self.parent, text='Kill', style='Accent.TButton', command=self.kill_button_click
        )
        self.list_button = ttk.Button(
            self.parent, text='List', style='Accent.TButton', command=self.list_button_click
        )
        self.list_frame = ttk.LabelFrame(self.parent, padding=(5, 5))
        self.scrollbar = ttk.Scrollbar(self.list_frame)
        self.scrollbar.pack(side="right", fill="y")
        self.list = ttk.Treeview(
            self.list_frame, selectmode='browse', yscrollcommand=self.scrollbar.set,
        )
        self.scrollbar.config(command=self.list.yview)
        self.list['columns'] = ('name', 'id', 'thread_count')
        self.list['show'] = 'headings'
        self.list.column('name', stretch=tk.NO)
        self.list.column('id', stretch=tk.NO)
        self.list.column('thread_count', stretch=tk.NO)

        # Sort feature for each column
        for col in self.list['columns']:
            self.list.heading(
                col, command=lambda _col=col: self.treeview_sort(_col, False)
            )


    def get_list(self):
        pass

    def run_button_click(self):
        pass

    def kill_button_click(self):
        pass

    def list_button_click(self):
        # Clear the list
        self.list.delete(*self.list.get_children())

        ls = self.get_list()
        if not ls:
            return
        
        idx = 0
        for item in ls:
            self.list.insert(
                parent='', index=idx, iid=idx, text='', values=item
            )
            idx += 1
    
    def treeview_sort(self, col, reverse):
        '''
            Sort by column
        '''
        if col in ['id', 'thread_count']:
            l = [(int(self.list.set(k, col)), k) for k in self.list.get_children()]
        else:
            l = [(self.list.set(k, col), k) for k in self.list.get_children()]

        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            self.list.move(k, '', index)

        # reverse sort next time
        self.list.heading(col, command=lambda _col=col: self.treeview_sort(_col, not reverse))