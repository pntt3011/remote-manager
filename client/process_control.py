from os import name
from socket import MsgFlag
from win32api import SendMessage
from base_control import BaseControl
import tkinter as tk
from tkinter import messagebox

class ProcessControl(BaseControl):
    def __init__(self, client, parent):
        super().__init__(client, parent)
        self.list_frame.configure(text='Process')
        self.list.heading('name', text='Process Name', anchor=tk.W)
        self.list.heading('id', text='Process ID', anchor=tk.W)
        self.list.heading('thread_count', text='Thread Count', anchor=tk.W)

    def get_list(self):
        if not self.client.send_signal('XEM_PROCESS'):
            return False
        
        return self.client.receive_obj()
    
    def run_button_click(self):
        pass

    def kill_button_click(self):
        item_cur = self.list.focus()
        if item_cur == "":
            messagebox.showerror(message="Please choose process.")
        else:
            process_id = self.list.item(item_cur)['values'][1]
            print(process_id, type(process_id))
            if not self.client.send_signal('KILL_PROCESS'):
                return
            if not self.client.send_signal(str(process_id)):
                return
            result = self.client.receive_signal()
            print(result)
            if result == "Killed":
                messagebox.showinfo(message='Process killed.')
            elif result == "Invalid application":
                messagebox.showerror(message='Process not found.')
            else:
                messagebox.showerror(message='An error occurs.')

    def list_button_click(self):
        return super().list_button_click()