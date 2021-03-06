from tkinter.constants import CENTER, HORIZONTAL, VERTICAL
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import messagebox
from ctypes import windll
import os
import cv2
import psutil
import shutil
import numpy as np
import tkinter as tk
import win32ui
import win32gui
import win32api
import win32con
import win32com.client
import win32comext.shell.shell as shell


class LocalFrame(tk.Frame):
    def __init__(self, parent, parent_frame, clipboard):
        super(LocalFrame, self).__init__(parent_frame)
        self.parent = parent
        self.conn = parent.connection
        self.clipboard = clipboard
        self.flag = True
        self.setup_components()
        self.setup_icons()
        self.reset_path()

    def setup_components(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=20)
        self.grid_columnconfigure(0, weight=1)

        self.add_path()
        self.add_treeview()
        self.add_scrollbar_to_widget(self.files, row=1, column=0)

    def add_path(self):
        field = tk.Frame(self)
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

        self.files.bind('<Double-Button-1>', self.on_double_click_item)
        self.files.bind('<Button-1>', self.on_click_item)

        self.setup_popup_menu()
        self.files.bind("<Button-3>", self.popup)

    def reset_selection(self):
        for item in self.files.selection():
            self.files.selection_remove(item)

    def on_double_click_item(self, event):
        iid = self.files.identify_row(event.y)
        if iid:
            self.files.focus(iid)
            self.files.selection_set(iid)
            curr_item = self.files.item(self.files.focus())
            dir_list = ['File folder', 'Disk Drive', '']

            if curr_item['values'][0] in dir_list:
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

        else:
            self.reset_selection()

    def on_click_item(self, event):
        iid = self.files.identify_row(event.y)
        if not iid:
            self.reset_selection()
            return "break"

        else:
            pass

    def setup_popup_menu(self):
        self.setup_file_popup()
        self.setup_empty_popup()

    def setup_file_popup(self):
        self.file_popup = tk.Menu(self, tearoff=0)
        self.file_popup.add_command(label="Open",
                                    command=self.open)
        self.file_popup.add_command(label="Open location",
                                    command=self.open_in_explorer)
        self.file_popup.add_command(label="Copy",
                                    command=self.copy)
        self.file_popup.add_command(label="Send to remote",
                                    command=self.send_to_remote)
        self.file_popup.add_command(label="Paste",
                                    command=self.paste)
        self.file_popup.add_command(label="Delete",
                                    command=self.delete_item)
        self.file_popup.entryconfig("Paste", state="disabled")

    def setup_empty_popup(self):
        self.empty_popup = tk.Menu(self, tearoff=0)
        self.empty_popup.add_command(label="Open location",
                                     command=self.open_in_explorer)
        self.empty_popup.add_command(label="Paste",
                                     command=self.paste)
        self.empty_popup.entryconfig("Paste", state="disabled")

    def popup(self, event):
        if self.clipboard[0] is not None:
            self.file_popup.entryconfig("Paste", state="active")
            self.empty_popup.entryconfig("Paste", state="active")

        iid = self.files.identify_row(event.y)
        if iid:
            self.files.focus(iid)
            type, _ = self.files.item(self.files.focus(), 'values')
            if type != '' and type != 'Disk Drive':
                selected = self.files.selection()
                if iid not in selected:
                    self.files.selection_set(iid)
                self.file_popup.post(event.x_root + 10, event.y_root)

        else:
            self.reset_selection()
            if self.last_path != '\\':
                self.empty_popup.post(event.x_root + 10, event.y_root)

    def open(self):
        paths = self.get_selected_path()
        try:
            for path in paths:
                os.startfile(path)

        except Exception as e:
            messagebox.showerror("Error", e)

    def open_in_explorer(self):
        windll.shell32.ShellExecuteW(
            None, 'open', 'explorer.exe', self.last_path, None, 1
        )

    def copy(self):
        paths = self.get_selected_path()
        self.clipboard[0] = self.flag
        self.clipboard[1] = paths

    def send_to_remote(self):
        paths = self.get_selected_path()
        remote_path = self.parent.remote_frame.last_path
        self.parent.remote_frame.send_over(paths, remote_path)

    def paste(self):
        dst = self.get_selected_path()[-1]
        if os.path.isfile(dst):
            dst = self.last_path

        srcs = self.clipboard[1]
        if self.flag == self.clipboard[0]:
            try:
                for src in srcs:
                    _, name = os.path.split(src)
                    full_dst = os.path.join(dst, name)

                    if os.path.isfile(src):
                        shutil.copyfile(src, full_dst)
                    else:
                        shutil.copytree(src, full_dst)

                messagebox.showinfo(
                    "Success", f"Copy {len(srcs)} items to {dst} successfully.")

            except Exception as e:
                messagebox.showerror("Error", e)

            self.open_path()

        else:
            self.send_over(srcs, dst)

    def delete_item(self):
        paths = self.get_selected_path()
        try:
            answer = messagebox.askyesno(title='Confirmation',
                                         message='Are you sure that you want to delete {} items?'.format(len(paths)))
            if answer:
                for path in paths:
                    if os.path.isdir(path):
                        shutil.rmtree(path)

                    elif os.path.isfile(path):
                        os.remove(path)
        except Exception as e:
            messagebox.showerror(
                "Error", e)
        finally:
            self.open_path()

    def get_selected_path(self):
        selected = self.files.selection()
        result = []

        for i in selected:
            curr_item = self.files.item(i)
            curr_dir = "" if self.last_path == "\\" else self.last_path
            selected_file = curr_item['text'][2:]

            if selected_file == "..":
                continue

            result.append(os.path.join(curr_dir, selected_file))

        if len(result) == 0:
            result.append(self.last_path)

        return result

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

    def setup_icons(self):
        self.icons = {}
        self.icons['File folder'] = self.get_icon("C:\\Windows")
        self.icons['Disk Drive'] = {}
        self.icons['Application'] = {}
        self.icons['Shortcut'] = {}

    def reset_path(self):
        self.set_path('\\')
        self.last_path = self.path.get()
        self.open_path()

    def get_drives(self):
        drps = psutil.disk_partitions()
        return [dp.device for dp in drps if dp.fstype == 'NTFS']

    def open_path(self):
        path = self.path.get()
        if not os.path.exists(path):
            self.set_path(self.last_path)
            return

        self.reset_treeview()
        self.last_path = path

        if path == "\\":
            for drive in self.get_drives():
                self.icons['Disk Drive'][drive] = self.get_icon(drive)
                self.files.insert(
                    parent='', index='end',
                    text='  ' + drive,
                    values=('Disk Drive', ''),
                    image=self.icons['Disk Drive'][drive]
                )

        else:
            self.files.insert(
                parent='', index='end',
                text='  ..',
                value=('', ''),
                image=self.icons['File folder']
            )

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
            image=self.icons['File folder']
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
            if file_type == "Application" or file_type == "Shortcut":
                self.icons[file_type][full_path] = self.get_icon(full_path)
                img = self.icons[file_type][full_path]

            else:
                if file_type == "File" or file_type not in self.icons:
                    self.icons[file_type] = self.get_icon(full_path)
                img = self.icons[file_type]

            self.files.insert(
                parent='', index='end',
                text='  ' + filename,
                value=(file_type, format(file_size, ',')),
                image=img
            )

    def set_path(self, s):
        self.path.delete(0, 'end')
        self.path.insert(0, s)

    def send_over(self, paths, local_path):
        self.conn.client.send_obj(["SEND", paths, local_path])
        s = self.conn.client.receive_obj()
        if s[0] == "RECEIVE":
            recv = self.conn.client.receive_item(s[1], True)
            if recv is None:
                messagebox.showinfo(
                    "Complete", "File transferred successfully.")

            else:
                messagebox.showerror(
                    "Error", "Error while transferring {}".format(s))

        else:
            messagebox.showerror(
                "Error", "Cannot start transferring")

        self.open_path()

    def get_icon(self, PATH):
        SHGFI_ICON = 0x000000100
        SHGFI_ICONLOCATION = 0x000001000
        # SHIL_SIZE = 0x00001 # 16x16
        SHIL_SIZE = 0x00002  # 32x32

        ret, info = shell.SHGetFileInfo(
            PATH, 0, SHGFI_ICONLOCATION | SHGFI_ICON | SHIL_SIZE)
        hIcon, iIcon, dwAttr, name, typeName = info
        ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_x)
        hdc = hdc.CreateCompatibleDC()
        hdc.SelectObject(hbmp)
        hdc.DrawIcon((0, 0), hIcon)
        win32gui.DestroyIcon(hIcon)

        bmpinfo = hbmp.GetInfo()
        bmpstr = hbmp.GetBitmapBits(True)
        icon = Image.frombuffer(
            "RGBA",
            (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
            bmpstr, "raw", "BGRA", 0, 1
        )

        # Resize with opencv because PIL resize is ugly
        icon = np.array(icon)
        icon = cv2.resize(icon, (19, 19))

        image = Image.fromarray(icon)
        img = ImageTk.PhotoImage(image)
        return img
