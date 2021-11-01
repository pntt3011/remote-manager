from LocalFrame import LocalFrame
from tkinter import messagebox
from PIL import Image, ImageTk
import tkinter as tk
import os
import cv2


class RemoteFrame(LocalFrame):
    def __init__(self, parent, clipboard):
        super(RemoteFrame, self).__init__(parent, clipboard)
        self.flag = False
        del self.icons['File folder']

    def reset_path(self):
        self.set_path('\\')
        self.last_path = self.path.get()

    def open_path(self):
        path = self.path.get()
        if not self.conn.client.send_obj(["OPEN", path]):
            self.path.configure(state='disabled')
            self.set_path(self.last_path)
            return

        self.path.configure(state='enabled')
        data = self.conn.client.receive_obj()

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
            image = Image.fromarray(item['icon'])

            if type == 'Disk Drive':
                self.icons[type][name] = ImageTk.PhotoImage(image)
                img = self.icons[type][name]

            elif type == 'Application':
                full_name = os.path.join(path, name)
                self.icons[type][full_name] = ImageTk.PhotoImage(image)
                img = self.icons[type][full_name]

            else:
                if type == 'File' or type not in self.icons:
                    self.icons[type] = ImageTk.PhotoImage(image)
                img = self.icons[type]

            self.files.insert(
                parent='', index='end',
                text='  ' + name,
                value=(type, size),
                image=img
            )

        self.files.yview_moveto(0)

    def setup_file_popup(self):
        self.file_popup = tk.Menu(self, tearoff=0)
        self.file_popup.add_command(label="Copy",
                                    command=self.copy)
        self.file_popup.add_command(label="Send to local",
                                    command=self.send_to_local)
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

    def send_to_local(self):
        paths = self.get_selected_path()
        local_path = self.parent.local_frame.last_path
        self.parent.local_frame.send_over(paths, local_path)

    def paste(self):
        dst = self.get_selected_path()[-1]
        if os.path.isfile(dst):
            dst = self.last_path

        if self.flag == self.clipboard[0]:
            src = self.clipboard[1]
            self.conn.client.send_obj(["COPY", src, dst])
            s = self.conn.client.receive_obj()

            if s[0] == "SUCCESS":
                messagebox.showinfo(
                    "Success", f"Copy {len(src)} item to {dst} successfully.")
            else:
                messagebox.showerror("Error", s[0])

            self.open_path()

        else:
            self.send_over(self.clipboard[1], dst)

    def delete_item(self):
        paths = self.get_selected_path()
        answer = messagebox.askyesno(title='Confirmation',
                                     message='Are you sure that you want to delete {} items?'.format(len(paths)))
        if not answer:
            return

        self.conn.client.send_obj(["DELETE", paths])
        s = self.conn.client.receive_obj()
        if s[0] == "SUCCESS":
            messagebox.showinfo(
                "Complete", "{} items have been deleted".format(len(paths)))
        else:
            messagebox.showerror(
                "Error", s[0])

        self.open_path()

    def send_over(self, paths, remote_path):
        for path in paths:
            if not os.path.exists(path):
                messagebox.showerror(
                    "Error", "{} does not exist".format(path))
                return

        self.conn.client.send_item(paths, remote_path, True)

        trans_result = self.conn.client.transfer_result
        if trans_result is None:
            s = self.conn.client.receive_obj()

            if s[0] == "SUCCESS":
                messagebox.showinfo(
                    "Complete", "Files transferred successfully.")

            else:
                messagebox.showerror(
                    "Error", "Error while transferring {}".format(s[0]))

        else:
            messagebox.showerror(
                "Error", trans_result)

        self.open_path()
