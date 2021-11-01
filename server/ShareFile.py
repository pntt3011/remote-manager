from ServerSocket import ServerSocket
from PIL import Image, ImageTk
import os
import cv2
import numpy as np
import psutil
import shutil
import pythoncom
import win32com.client
import win32ui
import win32gui
import win32api
import win32con
import win32com.client
import win32comext.shell.shell as shell


class ShareFile:
    def __init__(self, server: ServerSocket):
        self.server = server
        self.icons = {}
        self.icons['File folder'] = self.get_icon("C:\\Windows")
        self.icons['Disk Drive'] = {}
        self.icons['Application'] = {}
        self.icons['Shortcut'] = {}
        pythoncom.CoInitialize()

    def start_listening(self, s):
        if type(s) == type([]):
            if s[0] == "OPEN":
                files = self.get_files(s[1])
                self.server.send_obj(files)

            elif s[0] == "DELETE":
                path = s[1]
                s = self.delete_path(path)
                self.server.send_obj([s])

            elif s[0] == "RECEIVE":
                s = self.server.receive_item(s[1])
                if s is None:
                    self.server.send_obj(["SUCCESS"])

                else:
                    self.server.send_obj([s])

            elif s[0] == "SEND":
                self.server.send_item(s[1], s[2])

            elif s[0] == "COPY":
                s = self.copy_file(s[1], s[2])
                self.server.send_obj([s])

            else:
                return False

            return True

        else:
            return False

    def get_drives(self):
        drps = psutil.disk_partitions()
        return [dp.device for dp in drps if dp.fstype == 'NTFS']

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
        return icon

    def get_files(self, path):
        if not os.path.exists(path):
            return {}

        result = {}
        result['root'] = path
        result['files'] = []

        if path == "\\":
            for drive in self.get_drives():
                self.insert_drive(result['files'], drive)

        else:
            result['files'].append({
                'name': '..',
                'type': '',
                'size': '',
                'icon': self.icons['File folder']
            })

            for root, dirs, files in os.walk(path):
                for dir in dirs:
                    self.insert_folder(result['files'], dir)

                sh = win32com.client.gencache.EnsureDispatch(
                    'Shell.Application', 0)
                ns = sh.NameSpace(path)

                for file in files:
                    self.insert_file(result['files'], root, file, ns)

                break

        return result

    def insert_drive(self, dict, drive):
        self.icons['Disk Drive'][drive] = self.get_icon(drive)
        dict.append({
                    'name': drive,
                    'type': 'Disk Drive',
                    'size': '',
                    'icon': self.icons['Disk Drive'][drive]
                    })

    def insert_folder(self, dict, dir):
        dict.append({
            'name': dir,
            'type': 'File folder',
            'size': '',
            'icon': self.icons['File folder']
        })

    def insert_file(self, dict, root, filename, ns):
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

            dict.append({
                'name': filename,
                'type': file_type,
                'size': format(file_size, ','),
                'icon': img
            })

    def copy_file(self, srcs, dst):
        try:
            for src in srcs:
                _, name = os.path.split(src)
                full_dst = os.path.join(dst, name)

                if os.path.isfile(src):
                    shutil.copyfile(src, full_dst)
                else:
                    shutil.copytree(src, full_dst)

            return "SUCCESS"

        except Exception as e:
            return str(e)

    def delete_path(self, paths):
        try:
            for path in paths:
                if os.path.isdir(path):
                    shutil.rmtree(path)

                elif os.path.isfile(path):
                    os.remove(path)

                else:
                    return f"Invalid filename {path}"

            return "SUCCESS"

        except Exception as e:
            return str(e)
