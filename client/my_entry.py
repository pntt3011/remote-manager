from tkinter import ttk
import tkinter as tk

class MyEntry(ttk.Entry):
    def __init__(self, parent, alt, **kwargs):
        super().__init__(parent, **kwargs)
        self.alt = alt
        self.config(foreground='grey')
        self.insert(0, self.alt)

        def txt_in(e):
            ### Tkinter unknown
            # print(type(self.cget('foreground')))
            # print(self.cget('foreground'))
            # print(type(self.cget('foreground')))
            if str(self.cget('foreground')) == 'grey':
                self.config(foreground='black')
                self.delete(0,'end')

        def txt_out(e):
            if self.get() == '':
                self.delete(0, 'end')
                self.config(foreground='grey')
                self.insert(0, self.alt)

        self.bind("<FocusIn>", txt_in)
        self.bind("<FocusOut>", txt_out)

    def set_alt(self, alt):
        self.alt = alt

    def get(self):
        if str(self.cget('foreground')) == 'grey':
            return ''
        else:
            return super().get()
