from tkinter.constants import CENTER, HORIZONTAL, VERTICAL
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import messagebox
from ctypes import windll
import tkinter as tk
import os
import win32com.client
import psutil
import shutil


class LocalFrame(tk.Frame):
    def __init__(self, parent):
        super(LocalFrame, self).__init__(parent.share_files_tab)
        self.parent = parent
        self.client = parent.client
        self.setup_components()
        self.setup_files()

    def setup_components(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=20)
        self.grid_columnconfigure(0, weight=1)

        self.add_path()
        self.add_treeview()
        self.add_scrollbar_to_widget(self.files, row=1, column=0)

    def add_path(self):
        field = ttk.Frame(self)
        field.grid(row=0, column=0, sticky="ew")

        label = ttk.Label(field, text="Local path: ")
        label.pack(side="left")

        self.path = ttk.Entry(field)
        self.path.pack(side="left", expand=True, fill="both")
        self.path.bind("<Return>", lambda _: self.open_path())

    def add_treeview(self):
        self.files = ttk.Treeview(self)
        self.files['columns'] = ('Type', 'Size')
        self.files.column('#0', anchor='w', minwidth=100, width=300)
        self.files.column('Type', anchor='w', minwidth=100, width=100)
        self.files.column('Size', anchor='e', minwidth=100, width=100)

        self.files.heading('#0', text='Name', anchor=CENTER)
        self.files.heading('Type', text='Type', anchor=CENTER)
        self.files.heading('Size', text='Size', anchor=CENTER)

        self.files.bind('<Double-Button-1>',
                        lambda _: self.on_click_item())

        self.add_popup_menu()

    def on_click_item(self):
        curr_item = self.files.item(self.files.focus())

        if curr_item['values'][0] == 'File folder' or curr_item['values'][0] == 'Disk Drive':
            curr_dir = "" if self.last_path == "\\" else self.last_path
            new_file = curr_item['text'][2:]

            if new_file != "..":
                new_path = os.path.join(curr_dir, new_file)

            else:
                new_path, fn = os.path.split(curr_dir)
                if fn == "":
                    new_path = "\\"

            self.set_path(new_path)
            self.open_path()

    def add_popup_menu(self):
        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_command(label="Open file location",
                                    command=self.open_in_explorer)
        self.popup_menu.add_command(label="Send to Remote",
                                    command=self.send_to_remote)
        self.popup_menu.add_command(label="Delete",
                                    command=self.delete_item)

        self.files.bind("<Button-3>", self.popup)

    def popup(self, event):
        iid = self.files.identify_row(event.y)
        if iid:
            self.files.focus(iid)
            self.files.selection_set(iid)
            self.popup_menu.post(event.x_root + 10, event.y_root)
        else:
            pass

    def open_in_explorer(self):
        windll.shell32.ShellExecuteW(
            None, 'open', 'explorer.exe', self.last_path, None, 1
        )

    def delete_item(self):
        path = self.get_selected_path()
        try:
            if os.path.isdir(path):
                answer = messagebox.askyesno(title='Confirmation',
                                             message='Are you sure that you want to delete {}?'.format(path))
                if answer:
                    shutil.rmtree(path)

            elif os.path.isfile(path):
                answer = messagebox.askyesno(title='Confirmation',
                                             message='Are you sure that you want to delete {}?'.format(path))
                if answer:
                    os.remove(path)

            self.open_path()

        except:
            messagebox.showerror(
                "Delete Error", "Cannot delete this file/folder.")

    def get_selected_path(self):
        curr_item = self.files.item(self.files.focus())
        curr_dir = "" if self.last_path == "\\" else self.last_path
        selected_file = curr_item['text'][2:]

        if selected_file != "..":
            selected_path = os.path.join(curr_dir, selected_file)
            return selected_path
        return None

    def send_to_remote(self):
        path = self.get_selected_path()
        self.parent.remote_frame.send_over(path)

    def add_scrollbar_to_widget(self, widget, row=0, column=0):
        scroll_y = ttk.Scrollbar(self, orient=VERTICAL)
        scroll_y.grid(row=row, column=column+1, sticky="ns")

        scroll_x = ttk.Scrollbar(self, orient=HORIZONTAL)
        scroll_x.grid(row=row+1, column=column, sticky="ew")

        widget.configure(yscrollcommand=scroll_y.set)
        widget.configure(xscrollcommand=scroll_x.set)
        widget.grid(row=row, column=column, sticky="nsew")

        scroll_y.config(command=widget.yview)
        scroll_x.config(command=widget.xview)

    def setup_files(self):
        self.get_assets()
        self.get_drives()
        self.reset_path()

    def get_assets(self):
        asset_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), "assets")

        self.disk_icon = ImageTk.PhotoImage(
            Image.open(os.path.join(asset_path, "disk.png")))

        self.folder_icon = ImageTk.PhotoImage(
            Image.open(os.path.join(asset_path, "folder.png")))

        self.file_icon = ImageTk.PhotoImage(
            Image.open(os.path.join(asset_path, "file.png")))

    def get_drives(self):
        drps = psutil.disk_partitions()
        self.drives = [dp.device for dp in drps if dp.fstype == 'NTFS']

    def reset_path(self):
        self.set_path('\\')
        self.last_path = self.path.get()
        self.open_path()

    def open_path(self):
        path = self.path.get()
        if not os.path.exists(path):
            self.set_path(self.last_path)
            return

        self.reset_treeview()
        self.last_path = path

        if path == "\\":
            for drive in self.drives:
                self.files.insert(
                    parent='', index='end',
                    text='  ' + drive,
                    values=('Disk Drive', ''),
                    image=self.disk_icon
                )

        else:
            self.insert_folder(None, '..')

            for root, dirs, files in os.walk(path):
                for dir in dirs:
                    self.insert_folder(root, dir)

                sh = win32com.client.gencache.EnsureDispatch(
                    'Shell.Application', 0)
                ns = sh.NameSpace(path)

                for file in files:
                    self.insert_file(root, file, ns)

                break

        self.files.yview_moveto(0)

    def reset_treeview(self):
        self.files.delete(*self.files.get_children())

    def insert_folder(self, root, dirname):
        self.files.insert(
            parent='', index='end',
            text='  ' + dirname,
            value=('File folder', ''),
            image=self.folder_icon
        )

    def insert_file(self, root, filename, ns):
        full_path = os.path.join(root, filename)
        file_size = os.stat(full_path).st_size

        try:
            item = ns.ParseName(str(filename))
            file_type = ns.GetDetailsOf(item, 2)

            if file_type is not None:
                if file_type.endswith('bytes') \
                        or file_type.endswith('KB') \
                        or file_type.endswith('MB') \
                        or file_type.endswith('GB'):
                    file_type = ns.GetDetailsOf(item, 4)

            else:
                file_type = "File"

        except:
            file_type = "File"

        finally:
            self.files.insert(
                parent='', index='end',
                text='  ' + filename,
                value=(file_type, format(file_size, ',')),
                image=self.file_icon
            )

    def set_path(self, s):
        self.path.delete(0, 'end')
        self.path.insert(0, s)

    def send_over(self, path):
        local_path = self.last_path
        self.client.send_obj(["SEND", path, local_path])
        s = self.client.receive_obj()
        if s[0] == "RECEIVE":
            s = self.client.receive_item(s[1], True)
            if s is None:
                messagebox.showinfo(
                    "Complete", "File transferred successfully.")

            else:
                messagebox.showerror(
                    "Error", "Error while transferring {}".format(s))

        else:
            messagebox.showerror(
                "Error", "Cannot start transferring")

        self.open_path()
