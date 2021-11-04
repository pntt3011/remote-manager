from socket import MsgFlag
from win32api import SendMessage
from base_control import BaseControl
import tkinter as tk
from tkinter import messagebox


class ProcessControl(BaseControl):
    def __init__(self, conn, parent):
        super().__init__(conn, parent)
        self.list_frame.configure(text='Process')
        self.list.heading('name', text='Process Name', anchor=tk.W)
        self.list.heading('id', text='Process ID', anchor=tk.W)
        self.list.heading('thread_count', text='Thread Count', anchor=tk.W)
        self.entry.set_alt('Enter process name')

    def get_list(self):
        if not self.conn.client.send_obj('XEM_PROCESS'):
            return False

        return self.conn.client.receive_obj()

    def run_button_click(self):
        if self.entry.get() == '':
            messagebox.showerror(message='Please enter process name.')
            return

        if not self.conn.client.send_obj('START_PROCESS'):
            return
        if not self.conn.client.send_obj(self.entry.get()):
            return

        s = self.conn.client.receive_obj()
        if s == "Process started":
            messagebox.showinfo(message='Process started.')
            self.list_button_click()
        else:
            messagebox.showerror(message='An error occurs.')

    def kill_button_click(self):
        item_cur = self.list.focus()
        if item_cur == "":
            messagebox.showerror(message="Please choose process.")
        else:
            process_id = self.list.item(item_cur)['values'][1]
            print(process_id, type(process_id))
            if not self.conn.client.send_obj('KILL_PROCESS'):
                return
            if not self.conn.client.send_obj(str(process_id)):
                return
            result = self.conn.client.receive_obj()
            print(result)
            if result == "Killed":
                messagebox.showinfo(message='Process killed.')
            elif result == "Invalid application":
                messagebox.showerror(message='Process not found.')
            else:
                messagebox.showerror(message='An error occurs.')
            self.list_button_click()

    def list_button_click(self):
        return super().list_button_click()

    def setup_UI(self):
        super().setup_UI()
