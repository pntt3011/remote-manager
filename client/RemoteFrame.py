from LocalFrame import LocalFrame
from tkinter import messagebox
import tkinter as tk

import os


class RemoteFrame(LocalFrame):
    def __init__(self, parent, clipboard):
        super(RemoteFrame, self).__init__(parent, clipboard)
        self.flag = False

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

            if type == 'File folder' or name == '..':
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

    def setup_file_popup(self):
        self.file_popup = tk.Menu(self, tearoff=0)
        self.file_popup.add_command(label="Copy",
                                    command=self.copy)
        self.file_popup.add_command(label="Paste",
                                    command=self.paste)
        self.file_popup.add_command(label="Delete",
                                    command=self.delete_item)
        self.file_popup.entryconfig("Paste", state="disabled")

    def setup_empty_popup(self):
        self.empty_popup = tk.Menu(self, tearoff=0)
        self.empty_popup.add_command(label="Paste",
                                     command=self.paste)
        self.empty_popup.entryconfig("Paste", state="disabled")

    def paste(self):
        dst = self.get_selected_path()
        if os.path.isfile(dst):
            dst = self.last_path

        if self.flag == self.clipboard[0]:
            src = self.clipboard[1]
            self.client.send_obj(["COPY", src, dst])
            s = self.client.receive_obj()

            if s[0] == "SUCCESS":
                messagebox.showinfo(
                    "Success", f"Copy {src} to {dst} successfully.")
            else:
                messagebox.showerror("Error", f"Fail to copy {src} to {dst}.")

        else:
            self.send_over(self.clipboard[1], dst)

        self.open_path()

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

    def send_over(self, path, remote_path):
        if not os.path.exists(path):
            messagebox.showerror(
                "Error", "Error while transferring {}".format(path))

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
