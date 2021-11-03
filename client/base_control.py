from tkinter import Event, StringVar, Toplevel, ttk
import tkinter as tk
from my_entry import MyEntry

class BaseControl:
    def __init__(self, conn, parent):
        self.conn = conn
        self.parent=  parent
        self.run_frame = ttk.LabelFrame(
            self.parent, text='Run', padding=(5, 5)
        )
        self.entry = MyEntry(self.run_frame, '', justify='center')
        self.run_button = ttk.Button(
            self.run_frame, text='Start', style='Accent.TButton', command=self.run_button_click
        )
        self.list_button = ttk.Button(
            self.parent, text='List', style='Accent.TButton', command=self.list_button_click
        )
        self.list_frame = ttk.LabelFrame(self.parent, padding=(5, 5))
        self.scrollbar = ttk.Scrollbar(self.list_frame)
        self.list = ttk.Treeview(
            self.list_frame, selectmode='browse', yscrollcommand=self.scrollbar.set,
        )

        self.scrollbar.config(command=self.list.yview)
        column = ('name', 'id', 'thread_count')
        self.list['columns'] = column
        self.list['show'] = 'headings'
        self.list.bind("<Button-3>", self.popup)

        # Sort feature for each column
        for col in column:
            self.list.heading(
                col, command=lambda _col=col: self.treeview_sort(_col, False)
            )

        self.setup_popup()


    def setup_popup(self):
        self.item_popup = tk.Menu(tearoff=0)
        self.item_popup.add_command(label="Kill", command=self.kill_button_click)

    def popup(self, event):
        iid = self.list.identify_row(event.y)
        print(iid)
        if iid:
            self.list.selection_set(iid)
            self.list.focus(iid)
            self.item_popup.post(event.x_root, event.y_root)

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
            temp = list(item)
            temp[0] = temp[0].capitalize()
            self.list.insert(
                parent='', index=idx, iid=idx, text='', values=temp
            )
            idx += 1
        self.treeview_sort('name', False)
    
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

    def handle_lost_connection(self):
        self.list.delete(*self.list.get_children())

    def setup_UI(self):
        # Setup grid
        self.parent.rowconfigure(index=0, weight=1)
        self.parent.rowconfigure(index=1, weight=10000)
        self.parent.columnconfigure(index=0, weight=4)
        self.parent.columnconfigure(index=1, weight=1)
        self.parent.columnconfigure(index=2, weight=1)
        self.parent.columnconfigure(index=3, weight=50)

        # Put tkinter widgets into grid
        self.run_frame.grid(
            row=0, column=0, columnspan=1, padx=(5, 5), pady=(0, 0), sticky="nsew"
        )
        self.run_frame.columnconfigure(index=0, weight=3)
        self.run_frame.columnconfigure(index=1, weight=1)
        self.entry.grid(
            row=0, column=0, padx=(5, 5), pady=(0, 0), sticky="nsew"
        )
        self.run_button.grid(
            row=0, column=1, padx=(5, 5), pady=(0, 0), sticky="nsew"
        )
        self.list_button.grid(
            row=0, column=1, padx=(5, 5), pady=(22, 4), sticky="nsew"
        )
        self.list_frame.grid(
            row=1, column=0, columnspan=4, pady=(0, 0), sticky="nsew"
        )
        self.scrollbar.pack(side="right", fill="y")
        self.list.pack(fill='both', expand=True)