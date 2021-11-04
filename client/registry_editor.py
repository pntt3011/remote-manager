from tkinter import image_names, ttk, messagebox
from tkinter import scrolledtext as tkst
import tkinter as tk
from typing import Text
from my_entry import MyEntry
from tkinter import filedialog

class RegistryEditor:
    def __init__(self, parent, conn):
        self.parent = parent
        self.conn = conn
        self.my_style = ttk.Style(self.parent)
        self.my_style.configure('lefttab.TNotebook', tabposition='wn')
        self.my_style.map(
            'lefttab.TNotebook.Tab',
            background=[("selected", '#2780e3'), ("!selected", '#91C2F9')],
            foreground=[('selected', 'white'), ("!selected", 'white')]
        )
        self.my_style.map(
            'lefttab.TNotebook',
            background=[('!selected', '#E0E0E0')]
        )
        self.notebook = ttk.Notebook(self.parent, style='lefttab.TNotebook')
        self.import_tab = ttk.Frame(self.parent)
        self.notebook.add(self.import_tab, text='Import file registry')
        self.import_button = ttk.Button(
            self.import_tab, text='Import registry', command=self.handle_import_button
        )
        self.import_text = tkst.ScrolledText(self.import_tab, undo=True)
        self.browse_button = ttk.Button(
            self.import_tab, text='Browse', command=self.handle_browse_button
        )
        self.edit_tab = ttk.Frame(self.parent)
        self.notebook.add(self.edit_tab, text='Edit registry value')
        self.paned_windows = ttk.PanedWindow(self.edit_tab)
        self.edit_value_frame = ttk.LabelFrame(self.edit_tab, text='Edit registry value')
        self.paned_windows.add(self.edit_value_frame)
        self.function_type = ttk.Menubutton(
            self.edit_value_frame, text='Function'
        )
        self.edit_button = ttk.Button(
            self.edit_value_frame, text='Send', command=self.handle_edit_button
        )
        self.clear_button = ttk.Button(
            self.edit_value_frame, text='Clear', command=self.handle_clear_button
        )
        self.function_menu = tk.Menu(self.function_type)
        self.function_var = tk.StringVar()
        for function in ['Get value', 'Set value', 'Delete value', 'Create key', 'Delete key']:
            self.function_menu.add_radiobutton(label=function,
                                               value=function,
                                               variable=self.function_var,
                                               command=self.handle_choose_function)
        self.function_type['menu'] = self.function_menu
        self.path_entry = MyEntry(
            parent=self.edit_value_frame, alt='Enter registry file path'
        )
        self.name_value_entry = MyEntry(
            parent=self.edit_value_frame, alt='Name value'
        )
        self.value_entry = MyEntry(
            parent=self.edit_value_frame, alt='Value'
        )
        self.value_type = ttk.Menubutton(self.edit_value_frame, text='Type')
        self.type_menu = tk.Menu(self.value_type)
        self.type_var = tk.StringVar()
        for type in ['String', 'Binary', 'DWORD', 'Multi-String', 'Expandable string']:
            self.type_menu.add_radiobutton(label=type,
                                           value=type,
                                           variable=self.type_var,
                                           command=self.handle_choose_type)
        self.value_type['menu'] = self.type_menu
        self.log_frame = ttk.LabelFrame(self.edit_tab, text='Log')
        self.paned_windows.add(self.log_frame)
        self.log_text = tkst.ScrolledText(self.log_frame, state=tk.DISABLED)

    def handle_choose_function(self):
        s = self.function_var.get()
        self.function_type.configure(text=s)
        self.name_value_entry.grid_remove()
        self.value_type.grid_remove()
        self.value_entry.grid_remove()
        if s == 'Get value' or s == 'Delete value':
            self.name_value_entry.grid()
        elif s == 'Set value':
            self.name_value_entry.grid()
            self.value_entry.grid()
            self.value_type.grid()

    def handle_choose_type(self):
        s = self.type_var.get()
        self.value_type.configure(text=s)

    def add_edit_log(self, s):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(1.0, s + '\n')
        self.log_text.yview_moveto('0.0')
        self.log_text.config(state=tk.DISABLED)

    def handle_clear_button(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def handle_edit_button(self):
        if not self.function_var.get():
            self.add_edit_log('Error: Function type has not been chosen yet.')
            return
        elif self.function_var.get() == 'Set value' and not self.type_var.get():
            self.add_edit_log('Error: Var type has not been chosen yet.')
            return

        if not self.conn.client.send_obj('SEND'):
            return

        data = [self.function_var.get(),
                self.path_entry.get(),
                self.name_value_entry.get(),
                self.value_entry.get(),
                self.type_var.get()]
        if not self.conn.client.send_obj(data):
            return
        
        s = self.conn.client.receive_obj()
        if s == 'Error':
            self.add_edit_log(self.function_var.get() + ': Error.')
        else:
            if self.function_var.get() == 'Get value':
                self.add_edit_log('Get value: ' + s)
            else:
                self.add_edit_log(self.function_var.get() + ': Success.')

    def handle_browse_button(self):
        filename = filedialog.askopenfilename(initialdir="/",
                                                 title='Open',
                                                 filetypes=(('Reg file', '*.reg'), ))
        try:
            f = open(filename, mode='r', encoding='utf-8')
            s = f.read()
            f.close()
        except UnicodeDecodeError:
            f = open(filename, mode='r', encoding='utf-16')
            s = f.read()
            f.close()
        except:
            s = ''
        self.import_text.delete(1.0, tk.END)
        self.import_text.insert(tk.END, s)

    def handle_import_button(self):
        if not self.conn.client.send_obj('REG'):
            return
        if not self.conn.client.send_obj(self.import_text.get("1.0", tk.END)):
            return

        s = self.conn.client.receive_obj()
        if s == "Success":
            messagebox.showinfo(message="Import successfully.")
        else:
            messagebox.showerror(message="Failed to import!")

    def handle_lost_connection(self):
        self.import_text.delete(1.0, tk.END)
        self.function_var.set('')
        self.function_type.configure(text='Function')
        self.path_entry.delete(0, tk.END)
        self.name_value_entry.delete(0, tk.END)
        self.value_entry.delete(0, tk.END)
        self.value_type.configure(text='Type')
        self.type_var.set('')
        self.handle_clear_button()

    def setup_UI(self):
        # Setup grid
        self.notebook.pack(fill='both', expand=True)
        self.import_tab.rowconfigure(index=0, weight=1)
        self.import_tab.rowconfigure(index=1, weight=100)
        self.import_tab.columnconfigure(index=0, weight=1)
        self.import_tab.columnconfigure(index=1, weight=1)
        self.import_tab.columnconfigure(index=2, weight=10)
        self.paned_windows.pack(fill='both', expand=True)
        self.edit_value_frame.rowconfigure(index=0, weight=1)
        self.edit_value_frame.rowconfigure(index=1, weight=1)
        self.edit_value_frame.rowconfigure(index=2, weight=1)
        self.edit_value_frame.columnconfigure(index=0, weight=2)
        self.edit_value_frame.columnconfigure(index=1, weight=2)
        self.edit_value_frame.columnconfigure(index=2, weight=2)

        # # Put tkinter widgets into grid
        self.browse_button.grid(
            row=0, column=0, padx=(5, 5), pady=(5, 5), sticky='nsew'
        )
        self.import_button.grid(
            row=0, column=1, padx=(5, 5), pady=(5, 5), sticky='nsew'
        )
        self.import_text.grid(
            row=1, column=0, columnspan=3, padx=(2, 2), pady=(2, 2), sticky='nsew'
        )
        self.function_type.grid(
            row=0, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky='nsew'
        )
        self.path_entry.grid(
            row=1, column=0, columnspan=2, padx=(2, 2), pady=(2, 2), sticky='nsew'
        )
        self.name_value_entry.grid(
            row=2, column=0, padx=(2, 2), pady=(2, 2), sticky='nsew'
        )
        self.value_entry.grid(
            row=2, column=1, padx=(2, 2), pady=(2, 2), sticky='nsew'
        )
        self.value_type.grid(
            row=2, column=2, padx=(2, 2), pady=(2, 2), sticky='nsew'
        )
        self.edit_button.grid(
            row=0, column=2, padx=(2, 2), pady=(2, 2), sticky='nsew'
        )
        self.clear_button.grid(
            row=1, column=2, padx=(2, 2), pady=(2, 2), sticky='nsew'
        )
        self.log_text.pack(fill='both', expand=True)