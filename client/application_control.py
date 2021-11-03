from os import name
from socket import MsgFlag
from win32api import SendMessage
from base_control import BaseControl
import tkinter as tk
from tkinter import messagebox


class ApplicationControl(BaseControl):
    def __init__(self, conn, parent):
        super().__init__(conn, parent)
        self.list_frame.configure(text='Application')
        self.list.heading('name', text='Application Name', anchor=tk.W)
        self.list.heading('id', text='Appliction ID', anchor=tk.W)
        self.list.heading('thread_count', text='Thread Count', anchor=tk.W)
        self.entry.set_alt('Enter application name')

    def get_list(self):
        if not self.conn.client.send_obj('XEM_APP'):
            return False

        return self.conn.client.receive_obj()

    def run_button_click(self):
        if self.entry.get() == '':
            messagebox.showerror(message='Please enter application name.')
            return
    
        if not self.conn.client.send_obj('START_APP'):
            return
        if not self.conn.client.send_obj(self.entry.get()):
            return

        s = self.conn.client.receive_obj()
        if s == "Process started":
            messagebox.showinfo(message='Application started.')
            self.list_button_click()
        else:
            messagebox.showerror(message='An error occurs.')

    def kill_button_click(self):
        item_cur = self.list.focus()
        if item_cur == "":
            messagebox.showerror(message="Please choose application.")
        else:
            application_id = self.list.item(item_cur)['values'][1]
            print(application_id, type(application_id))
            if not self.conn.client.send_obj('KILL_APP'):
                return
            if not self.conn.client.send_obj(str(application_id)):
                return
            result = self.conn.client.receive_obj()
            print(result)
            if result == "Killed":
                messagebox.showinfo(message='Application killed.')
            elif result == "Invalid application":
                messagebox.showerror(message='Application not found.')
            else:
                messagebox.showerror(message='An error occurs.')
            self.list_button_click()

    def list_button_click(self):
        return super().list_button_click()

    def setup_UI(self):
        super().setup_UI()
