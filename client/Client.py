from socket import socket, AF_INET, SOCK_STREAM
import tkinter as tk
from tkinter.constants import S
import tkinter.scrolledtext as tkst
from tkinter import messagebox, ttk
from tkinter.filedialog import asksaveasfile
from struct import unpack, pack
import pickle
import sys
from StreamingServer import StreamingServer
import threading

PORT = 8080
BUFFER_SIZE = 4096
HEADER_SIZE = 8


class Client:
    def __init__(self):
        self.ip = None
        self.client = None
        self.sender = None
        self.init_components()
        self.parent = {}

    def init_components(self):
        self.root = tk.Tk()
        self.root.title("Client")
        self.root.geometry("372x302")
        self.root.resizable(False, False)

        # txtIP
        self.txtIP = tk.Entry(self.root, state=tk.NORMAL)
        self.txtIP.place(height=20, width=226, x=12, y=29)

        # butConnect
        self.butConnect = tk.Button(
            text='Kết nối', command=self.butConnect_click)
        self.butConnect.place(height=23, width=100, x=244, y=27)

        # butApp
        self.butApp = tk.Button(text='App Running', command=self.butApp_click)
        self.butApp.place(height=63, width=145, x=93, y=64)

        # butTat
        self.butTat = tk.Button(text='Tắt máy', command=self.butTat_click)
        self.butTat.place(height=57, width=48, x=93, y=133)

        # butReg
        self.butReg = tk.Button(text='Sửa registry', command=self.butReg_click)
        self.butReg.place(height=65, width=198, x=93, y=196)

        # butExit
        self.butExit = tk.Button(text='Thoát', command=self.butExit_click)
        self.butExit.place(height=65, width=47, x=297, y=196)

        # butPic
        self.butPic = tk.Button(text='Chụp màn hình',
                                command=self.butPic_click)
        self.butPic.place(height=57, width=91, x=147, y=133)

        # butKeyLock
        self.butKeyLock = tk.Button(
            text='Keystroke', command=self.butKeyLock_click)
        self.butKeyLock.place(height=126, width=100, x=244, y=64)

        # butProcess
        self.butProcess = tk.Button(
            text='Process\nRunning', command=self.butProcess_click)
        self.butProcess.place(height=197, width=75, x=12, y=64)

    def solve_connection_disrupted(self):
        for w in self.root.winfo_children():
            if isinstance(w, tk.Toplevel):
                w.destroy()

        if self.client:
            self.client.close()
            self.client = None

        self.root.wm_attributes("-disabled", False)
        messagebox.showerror(
            message='Kết nối đến server bị gián đoạn! Vui lòng kết nối lại.')

    def send_msg(self, msg):
        try:
            self.client.sendall(bytes(msg, 'utf8'))
            return True
        except:
            self.solve_connection_disrupted()
            return False

    def receive_msg(self):
        return self.client.recv(BUFFER_SIZE).decode('utf8')

    def receive_obj(self):
        msg = bytearray()
        header = self.client.recv(HEADER_SIZE)
        (length,) = unpack('>Q', header)

        length_recv = 0
        while length_recv < length:
            s = self.client.recv(BUFFER_SIZE)
            msg += s
            length_recv += len(s)

        return pickle.loads(msg)

    def send_obj(self, obj):
        msg = pickle.dumps(obj)
        length = pack('>Q', len(msg))
        try:
            self.client.sendall(length)
            self.client.sendall(msg)
            return True
        except:
            self.solve_connection_disrupted()
            return False

    def quit_window(self, win):
        def call_quit():
            try:
                self.parent[win].wm_attributes("-disabled", False)
            except:
                pass

            if self.sender != None:
                self.sender.stop_server()

            try:
                self.send_msg('QUIT')
            finally:
                win.destroy()
        win.protocol("WM_DELETE_WINDOW", call_quit)

    def butConnect_click(self):
        if self.client:
            messagebox.showwarning(message='Đã kết nối đến server!')
            return

        self.client = socket(AF_INET, SOCK_STREAM)
        serverAddress = (self.txtIP.get(), PORT)
        try:
            self.client.connect(serverAddress)
            messagebox.showinfo(message='Kết nối đến server thành công!')
            self.ip = self.txtIP.get()
        except:
            messagebox.showerror(message='Lỗi kết nối đến server!')
            self.client = None

    def butTat_click(self):
        if self.client == None:
            messagebox.showerror(message='Chưa kết nối đến server!')
            return
        self.send_msg('SHUTDOWN')

    def butPic_click(self):
        if self.client == None:
            messagebox.showerror(message='Chưa kết nối đến server!')
            return

        if not self.send_msg('TAKEPIC'):
            return

        pic = tk.Toplevel(self.root)
        self.parent[pic] = self.root

        pic.title('pic')
        pic.geometry('900x510')
        pic.resizable(False, False)
        pic.transient(self.root)
        self.parent[pic].wm_attributes("-disabled", True)

        # Picture
        self.picture = tk.Label(pic)
        self.takePicButton_click()
        self.picture.place(width=720, height=405, x=12, y=22)

        # Quit TAKEPIC
        self.quit_window(pic)

    def takePicButton_click(self):
        self.sender = StreamingServer(self.ip, 9999, self.picture)
        self.sender.start_server()

    def savePicButton_click(self):
        files = [('Bitmap file', '*.bmp')]
        filename = asksaveasfile(
            mode='wb', defaultextension=files, filetypes=files)
        if filename:
            self.savedPicture.save(filename)

    def butProcess_click(self):
        if self.client == None:
            messagebox.showerror(message='Chưa kết nối đến server!')
            return

        # process window
        if not self.send_msg('PROCESS'):
            return

        self.process = tk.Toplevel(self.root)
        self.parent[self.process] = self.root
        self.process.title('Process')
        self.process.geometry('302x261')
        self.process.resizable(False, False)
        self.process.transient(self.root)
        self.parent[self.process].wm_attributes("-disabled", True)

        # killButton
        killButton = tk.Button(self.process, text='Kill',
                               command=self.killProcessButton_click)
        killButton.place(width=66, height=47, x=24, y=12)

        # xemButton
        xemButton = tk.Button(self.process, text='Xem',
                              command=self.xemProcessButton_click)
        xemButton.place(width=59, height=47, x=96, y=12)

        # startButton
        startButton = tk.Button(
            self.process, text='Start', command=self.startProcessButton_click)
        startButton.place(width=59, height=47, x=231, y=12)

        # delButton
        delButton = tk.Button(self.process, text='Xóa',
                              command=self.delProcessButton_click)
        delButton.place(width=64, height=47, x=161, y=12)

        # processList
        self.processList = ttk.Treeview(self.process)
        self.processList.place(width=266, height=162, x=24, y=74)
        self.processList['columns'] = ('1', '2', '3')
        self.processList['show'] = 'headings'
        self.processList.column('1', width=100, stretch=tk.NO)
        self.processList.column('2', width=65, stretch=tk.NO)
        self.processList.column('3', width=85, stretch=tk.NO)
        self.processList.heading('1', text='Name Process', anchor=tk.W)
        self.processList.heading('2', text='ID Process', anchor=tk.W)
        self.processList.heading('3', text='Count Thread', anchor=tk.W)
        vsb = ttk.Scrollbar(self.processList,
                            orient='vertical',
                            command=self.processList.yview)
        vsb.pack(side='right', fill='both')
        self.processList.configure(yscrollcommand=vsb.set)

        # Quit PROCESS
        self.quit_window(self.process)

    def xemProcessButton_click(self):
        self.processList.delete(*self.processList.get_children())
        if not self.send_msg('XEM'):
            return

        processls = self.receive_obj()
        idx = 0
        for x in processls:
            self.processList.insert(
                parent='', index=idx, iid=idx, text='', values=x)
            idx += 1

    def delProcessButton_click(self):
        self.processList.delete(*self.processList.get_children())

    def killProcessButton_click(self):
        # killProcess window
        if not self.send_msg('KILL'):
            return
        killProcess = tk.Toplevel(self.process)
        self.parent[killProcess] = self.process
        killProcess.title('Kill')
        killProcess.geometry('284x45')
        killProcess.resizable(False, False)
        killProcess.transient(self.process)
        self.parent[killProcess].wm_attributes("-disabled", True)

        # txtID
        txtID = tk.Entry(killProcess)
        txtID.insert(-1, 'Nhập ID')
        txtID.place(width=183, height=20, x=13, y=13)

        def kill():
            if (not self.send_msg('KILLID')) or (not self.send_msg(txtID.get())):
                return
            s = self.receive_msg()
            if s == "Killed":
                messagebox.showinfo(message='Đã diệt process!')
            elif s == "Invalid process":
                messagebox.showerror(message='Không tìm thấy process!')
            else:
                messagebox.showerror(message='Đã xảy ra lỗi!')
        # butKill
        butKill = tk.Button(killProcess, text='Kill', command=kill)
        butKill.place(width=75, height=23, x=202, y=13)

        # Quit KILL PROCESS
        self.quit_window(killProcess)

    def startProcessButton_click(self):
        # startProcess window
        if not self.send_msg('START'):
            return

        startProcess = tk.Toplevel(self.process)
        self.parent[startProcess] = self.process
        startProcess.title('Start')
        startProcess.geometry('284x45')
        startProcess.resizable(False, False)
        startProcess.transient(self.process)
        self.parent[startProcess].wm_attributes("-disabled", True)

        # processName
        processName = tk.Entry(startProcess)
        processName.insert(-1, 'Nhập tên')
        processName.place(width=183, height=20, x=13, y=13)

        def start_pro():
            if not self.send_msg('STARTID'):
                return

            if processName.get() == '':
                messagebox.showerror(message='Chưa nhập tên process!')
                return

            if not self.send_msg(processName.get()):
                return

            s = self.receive_msg()
            if s == "Process started":
                messagebox.showinfo(message='Process đã được bật!')
            else:
                messagebox.showerror(message='Đã xảy ra lỗi!')
        # butStart
        butStart = tk.Button(startProcess, text='Start', command=start_pro)
        butStart.place(width=75, height=23, x=202, y=13)

        # Quit START PROCESS
        self.quit_window(startProcess)

    def butApp_click(self):
        if self.client == None:
            messagebox.showerror(message='Chưa kết nối đến server!')
            return

        # app window
        if not self.send_msg('APPLICATION'):
            return

        self.app = tk.Toplevel(self.root)
        self.parent[self.app] = self.root
        self.app.title('listApp')
        self.app.geometry('302x261')
        self.app.resizable(False, False)
        self.app.transient(self.root)
        self.parent[self.app].wm_attributes("-disabled", True)

        # killButton
        killButton = tk.Button(self.app, text='Kill',
                               command=self.killAppButton_click)
        killButton.place(width=66, height=47, x=24, y=12)

        # xemButton
        xemButton = tk.Button(self.app, text='Xem',
                              command=self.xemAppButton_click)
        xemButton.place(width=59, height=47, x=96, y=12)

        # startButton
        startButton = tk.Button(self.app, text='Start',
                                command=self.startAppButton_click)
        startButton.place(width=59, height=47, x=231, y=12)

        # delButton
        delButton = tk.Button(self.app, text='Xóa',
                              command=self.delAppButton_click)
        delButton.place(width=64, height=47, x=161, y=12)

        # appList
        self.appList = ttk.Treeview(self.app)
        self.appList.place(width=266, height=162, x=24, y=74)
        self.appList['columns'] = ('1', '2', '3')
        self.appList['show'] = 'headings'
        self.appList.column('1', width=105, stretch=tk.NO)
        self.appList.column('2', width=85, stretch=tk.NO)
        self.appList.column('3', width=80, stretch=tk.NO)
        self.appList.heading('1', text='Name Application', anchor=tk.W)
        self.appList.heading('2', text='ID Application', anchor=tk.W)
        self.appList.heading('3', text='Count Thread', anchor=tk.W)
        vsb = ttk.Scrollbar(self.appList,
                            orient='vertical',
                            command=self.appList.yview)
        vsb.pack(side='right', fill='both')
        self.appList.configure(yscrollcommand=vsb.set)

        # Quit APP
        self.quit_window(self.app)

    def xemAppButton_click(self):
        self.appList.delete(*self.appList.get_children())

        if not self.send_msg('XEM'):
            return

        appls = self.receive_obj()
        idx = 0
        for x in appls:
            self.appList.insert(parent='', index=idx,
                                iid=idx, text='', values=x)
            idx += 1

    def delAppButton_click(self):
        self.appList.delete(*self.appList.get_children())

    def killAppButton_click(self):
        # killApp window
        if not self.send_msg('KILL'):
            return

        killApp = tk.Toplevel(self.app)
        self.parent[killApp] = self.app
        killApp.title('Kill')
        killApp.geometry('284x45')
        killApp.resizable(False, False)
        killApp.transient(self.app)
        self.parent[killApp].wm_attributes("-disabled", True)

        # txtID
        txtID = tk.Entry(killApp)
        txtID.insert(-1, 'Nhập ID')
        txtID.place(width=183, height=20, x=13, y=13)

        def kill():
            if (not self.send_msg('KILLID')) or (not self.send_msg(txtID.get())):
                return

            s = self.receive_msg()
            if s == "Killed":
                messagebox.showinfo(message='Đã diệt chương trình!')
            elif s == "Invalid application":
                messagebox.showerror(message='Không tìm thấy chương trình!')
            else:
                messagebox.showerror(message='Đã xảy ra lỗi!')
        # butKill
        butKill = tk.Button(killApp, text='Kill', command=kill)
        butKill.place(width=75, height=23, x=202, y=13)

        # Quit KILL APP
        self.quit_window(killApp)

    def startAppButton_click(self):
        # startApp window
        if not self.send_msg('START'):
            return

        startApp = tk.Toplevel(self.app)
        self.parent[startApp] = self.app
        startApp.title('Start')
        startApp.geometry('284x45')
        startApp.resizable(False, False)
        startApp.transient(self.app)
        self.parent[startApp].wm_attributes("-disabled", True)

        # appName
        appName = tk.Entry(startApp)
        appName.insert(-1, 'Nhập tên')
        appName.place(width=183, height=20, x=13, y=13)

        def start_app():
            if not self.send_msg('STARTID'):
                return

            if appName.get() == '':
                messagebox.showerror(message='Chưa nhập tên chương trình!')
                return

            if not self.send_msg(appName.get()):
                return

            s = self.receive_msg()
            if s == "Process started":
                messagebox.showinfo(message='Chương trình đã được bật!')
            else:
                messagebox.showerror(message='Đã xảy ra lỗi!')
        # butStart
        butStart = tk.Button(startApp, text='Start', command=start_app)
        butStart.place(width=75, height=23, x=202, y=13)

        # Quit START APP
        self.quit_window(startApp)

    def butKeyLock_click(self):
        if self.client == None:
            messagebox.showerror(message='Chưa kết nối đến server!')
            return

        # Keylog
        if not self.send_msg('KEYLOG'):
            return

        self.keylog = tk.Toplevel(self.root)
        self.parent[self.keylog] = self.root
        self.keylog.title('Keystroke')
        self.keylog.geometry('347x271')
        self.keylog.resizable(False, False)
        self.keylog.transient(self.root)
        self.parent[self.keylog].wm_attributes("-disabled", True)
        self.is_hooking = False
        # hookButton
        hookButton = tk.Button(self.keylog, text='Hook',
                               command=self.hookButton_click)
        hookButton.place(width=75, height=59, x=12, y=12)

        # unhookButton
        unhookButton = tk.Button(
            self.keylog, text='Unhook', command=self.unhookButton_click)
        unhookButton.place(width=75, height=59, x=93, y=12)

        # delButton
        delButton = tk.Button(self.keylog, text='Xóa',
                              command=self.delKeylogButton_click)
        delButton.place(width=75, height=59, x=256, y=12)

        # txtKQ
        self.txtKQ = tkst.ScrolledText(self.keylog, state=tk.DISABLED)
        self.txtKQ.place(width=318, height=182, x=12, y=77)

        self.quit_window(self.keylog)

    def hookButton_click(self):
        self.txtKQ.config(state=tk.NORMAL)
        self.txtKQ.config(state=tk.DISABLED)
        if not self.send_msg('HOOK'):
            return

        s = self.receive_msg()
        if s == "Success":
            messagebox.showinfo(message="Hook thành công!")
        else:
            messagebox.showerror(message="Hook thất bại!")

        self.is_hooking = True
        threading.Thread(target=self.printKeylogButton_click).start()

    def unhookButton_click(self):
        self.is_hooking = False
        self.send_msg('UNHOOK')

    def printKeylogButton_click(self):
        while self.is_hooking:
            if not self.send_msg('PRINT'):
                return

            s = self.receive_obj()
            self.txtKQ.config(state=tk.NORMAL)
            self.txtKQ.insert(tk.END, s)
            self.txtKQ.config(state=tk.DISABLED)

    def delKeylogButton_click(self):
        self.txtKQ.config(state=tk.NORMAL)
        self.txtKQ.delete(1.0, tk.END)
        self.txtKQ.config(state=tk.DISABLED)

    def butReg_click(self):
        if self.client == None:
            messagebox.showerror(message='Chưa kết nối đến server!')
            return

        # registry window
        if not self.send_msg('REGISTRY'):
            return

        reg = tk.Toplevel(self.root)
        self.parent[reg] = self.root
        reg.title('registry')
        reg.geometry('398x354')
        reg.resizable(False, False)
        reg.transient(self.root)
        self.parent[reg].wm_attributes("-disabled", True)

        # txtReg
        self.txtReg = tkst.ScrolledText(reg)
        self.txtReg.place(width=311, height=77, x=2, y=55)
        self.txtReg.insert(tk.END, 'Nội dung')
        self.txtReg.configure(font=("calibri", 10))

        # txtBro
        self.txtBro = tk.Entry(reg)
        self.txtBro.place(width=311, height=20, x=2, y=23)
        self.txtBro.insert(tk.END, 'Đường dẫn ...')

        # butBro
        butBro = tk.Button(reg, text='Browser...',
                           command=self.browseRegFile_click)
        butBro.place(width=75, height=23, x=319, y=20)

        # butSendContext
        butSendContext = tk.Button(
            reg, text='Gởi nội dung', command=self.sendContext_click)
        butSendContext.place(width=75, height=77, x=319, y=55)

        # groupBox
        groupBox = tk.LabelFrame(reg, text='Sửa giá trị trực tiếp')
        groupBox.place(width=384, height=204, x=2, y=138)

        # txtLog
        self.txtLog = tkst.ScrolledText(groupBox, state=tk.DISABLED)
        self.txtLog.place(width=372, height=68, x=6, y=82)
        self.txtLog.configure(font=("calibri", 10))

        # optionMenu
        optionList = ['Get value',
                      'Set value',
                      'Delete value',
                      'Create key',
                      'Delete key']
        self.var = tk.StringVar(groupBox)
        self.var.set('Chọn chức năng')
        optionMenu = tk.OptionMenu(groupBox, self.var, *optionList)
        optionMenu.place(width=372, height=25, x=6, y=0)

        def callback(*args):
            dict = {'Get value': self.get_value_reg_place,
                    'Set value': self.set_value_reg_place,
                    'Delete value': self.delete_value_reg_place,
                    'Create key': self.create_key_reg_place,
                    'Delete key': self.delete_key_reg_place}
            dict[self.var.get()]()
        self.var.trace("w", callback)

        # txtValue
        self.txtValue = tk.Entry(groupBox)
        self.place_txtValue()
        self.txtValue.insert(tk.END, "Value")

        # txtNameValue
        self.txtNameValue = tk.Entry(groupBox)
        self.place_txtNameValue()
        self.txtNameValue.insert(tk.END, "Name Value")

        # txtLink
        self.txtLink = tk.Entry(groupBox)
        self.txtLink.place(width=372, height=20, x=6, y=29)
        self.txtLink.insert(tk.END, 'Đường dẫn')

        # opType
        optionType = ['String',
                      'Binary',
                      'DWORD',
                      'QWORD',
                      'Multi-String',
                      'Expandable String']
        self.varType = tk.StringVar(groupBox)
        self.varType.set('Kiểu dữ liệu')
        self.opTypeMenu = tk.OptionMenu(groupBox, self.varType, *optionType)
        self.place_opTypeMenu()

        # butDel
        def delLog():
            self.txtLog.config(state=tk.NORMAL)
            self.txtLog.delete(1.0, tk.END)
            self.txtLog.config(state=tk.DISABLED)
        butDel = tk.Button(groupBox, text='Xóa', command=delLog)
        butDel.place(width=94, height=23, x=192, y=156)

        # butSend
        butSend = tk.Button(groupBox, text='Gởi', command=self.butSend_click)
        butSend.place(width=97, height=23, x=69, y=156)

        # call quit REGISTRY
        self.quit_window(reg)

    def insertLog(self, s):
        self.txtLog.config(state=tk.NORMAL)
        self.txtLog.insert(tk.END, s)
        self.txtLog.config(state=tk.DISABLED)

    def butSend_click(self):
        if self.var.get() == 'Chọn chức năng':
            self.insertLog('Lỗi\n')
            return
        elif self.var.get() == 'Set value' and self.varType.get() == 'Kiểu dữ liệu':
            self.insertLog('Lỗi\n')
            return

        if not self.send_msg('SEND'):
            return

        data = [self.var.get(),
                self.txtLink.get(),
                self.txtNameValue.get(),
                self.txtValue.get(),
                self.varType.get()]
        if not self.send_obj(data):
            return

        s = self.receive_obj()
        if s == 'Error':
            self.insertLog('Lỗi\n')
        else:
            if self.var.get() == 'Get value':
                self.insertLog(s)
                self.insertLog('\n')
            elif self.var.get() == 'Set value':
                self.insertLog('Set value thành công\n')
            elif self.var.get() == 'Delete value':
                self.insertLog('Delete value thành công\n')
            elif self.var.get() == 'Create key':
                self.insertLog('Create key thành công\n')
            elif self.var.get() == 'Delete key':
                self.insertLog('Delete key thành công\n')

    def place_txtValue(self):
        self.txtValue.place(width=138, height=20, x=125, y=55)

    def place_txtNameValue(self):
        self.txtNameValue.place(width=113, height=20, x=6, y=55)

    def place_opTypeMenu(self):
        self.opTypeMenu.place(width=109, height=25, x=269, y=52)

    def browseRegFile_click(self):
        filename = tk.filedialog.askopenfilename(initialdir="/",
                                                 title='Open',
                                                 filetypes=(('Reg file', '*.reg'), ))
        self.txtBro.delete(0, tk.END)
        self.txtBro.insert(tk.END, filename)
        try:
            f = open(self.txtBro.get(), mode='r', encoding='utf-8')
            s = f.read()
        except UnicodeDecodeError:
            f = open(self.txtBro.get(), mode='r', encoding='utf-16')
            s = f.read()
        f.close()
        self.txtReg.delete(1.0, tk.END)
        self.txtReg.insert(tk.END, s)

    def get_value_reg_place(self):
        self.txtValue.place_forget()
        self.opTypeMenu.place_forget()
        self.place_txtNameValue()

    def set_value_reg_place(self):
        self.place_opTypeMenu()
        self.place_txtNameValue()
        self.place_txtValue()

    def delete_value_reg_place(self):
        self.get_value_reg_place()

    def create_key_reg_place(self):
        self.txtValue.place_forget()
        self.opTypeMenu.place_forget()
        self.txtNameValue.place_forget()

    def delete_key_reg_place(self):
        self.create_key_reg_place()

    def sendContext_click(self):
        if (not self.send_msg('REG')) or (not self.send_obj(self.txtReg.get("1.0", tk.END))):
            return

        s = self.receive_msg()
        if s == "Success":
            messagebox.showinfo(message="Sửa thành công!")
        else:
            messagebox.showerror(message="Sửa thất bại!")

    def butExit_click(self):
        if self.client:
            self.client.close()
        sys.exit()

    def run(self):
        self.root.mainloop()
        if self.client:
            self.client.close()


if __name__ == "__main__":
    client = Client()
    client.run()
