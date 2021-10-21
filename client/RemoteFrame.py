from LocalFrame import LocalFrame
from tkinter import messagebox
import tkinter as tk

import os


class RemoteFrame(LocalFrame):
    def __init__(self, parent):
        super(RemoteFrame, self).__init__(parent)

    def reset_path(self):
        self.set_path('\\')
        self.last_path = self.path.get()

    def open_path(self):
        path = self.path.get()
        if not self.client.send_obj(["OPEN", path]):
            self.path.configure(state='disabled')
            self.set_path(self.last_path)
            return

        self.path.configure(state='enabled')
        data = self.client.receive_obj()

        if data == None or 'root' not in data:
            messagebox.showerror("Error", "Invalid path.")
            self.set_path(self.last_path)
            return

        self.reset_treeview()
        self.last_path = path

        for item in data['files']:
            name = item['name']
            type = item['type']
            size = item['size']
            image = self.file_icon

            if type == 'File folder':
                image = self.folder_icon

            elif type == 'Disk Drive':
                image = self.disk_icon

            self.files.insert(
                parent='', index='end',
                text='  ' + name,
                value=(type, size),
                image=image
            )

        self.files.yview_moveto(0)

    def add_popup_menu(self):
        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_command(label="Send to Local",
                                    command=self.send_to_local)
        self.popup_menu.add_command(label="Delete",
                                    command=self.delete_item)

        self.files.bind("<Button-3>", self.popup)

    def delete_item(self):
        path = self.get_selected_path()
        answer = messagebox.askyesno(title='Confirmation',
                                     message='Are you sure that you want to delete {}?'.format(path))
        if not answer:
            return

        self.client.send_obj(["DELETE", path])

        if self.client.receive_obj()[0] == "SUCCESS":
            messagebox.showinfo("Complete", "{} has been deleted".format(path))
            self.open_path()

        else:
            messagebox.showerror(
                "Delete Error", "Cannot delete this file/folder.")

    def send_to_local(self):
        path = self.get_selected_path()
        self.parent.local_frame.send_over(path)

    def send_over(self, path):
        if not os.path.exists(path):
            messagebox.showerror(
                "Error", "Error while transferring {}".format(path))

        remote_path = self.last_path
        self.client.send_item(path, remote_path, True)

        trans_result = self.client.transfer_result
        if trans_result is None:
            s = self.client.receive_obj()

            if s[0] == "SUCCESS":
                messagebox.showinfo(
                    "Complete", "File transferred successfully.")

            else:
                messagebox.showerror(
                    "Error", "Error while transferring {}".format(s[0]))

        else:
            messagebox.showerror(
                "Error", trans_result)

        self.open_path()
