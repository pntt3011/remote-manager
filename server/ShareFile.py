from ServerSocket import ServerSocket
import socket
import os
import sys
import psutil
import shutil
from ctypes import windll
import pythoncom
import win32com.client


drps = psutil.disk_partitions()
drives = [dp.device for dp in drps if dp.fstype == 'NTFS']


def get_files(path):
    if not os.path.exists(path):
        return {}

    result = {}
    result['root'] = path
    result['files'] = []

    if path == "\\":
        for drive in drives:
            insert_drive(result['files'], drive)

    else:
        result['files'].append({
            'name': '..',
            'type': '',
            'size': ''
        })

        for root, dirs, files in os.walk(path):
            for dir in dirs:
                insert_folder(result['files'], dir)

            sh = win32com.client.gencache.EnsureDispatch(
                'Shell.Application', 0)
            ns = sh.NameSpace(path)

            for file in files:
                insert_file(result['files'], root, file, ns)

            break

    return result


def insert_drive(dict, drive):
    dict.append({
                'name': drive,
                'type': 'Disk Drive',
                'size': ''
                })


def insert_folder(dict, dir):
    dict.append({
        'name': dir,
        'type': 'File folder',
        'size': ''
    })


def insert_file(dict, root, filename, ns):
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
        dict.append({
            'name': filename,
            'type': file_type,
            'size': format(file_size, ',')
        })


def copy_file(src, dst):
    _, name = os.path.split(src)
    full_dst = os.path.join(dst, name)
    print(src)
    print(dst)
    print(full_dst)
    try:
        if os.path.isfile(src):
            shutil.copyfile(src, full_dst)
        else:
            shutil.copytree(src, full_dst)

        return True

    except:
        return False


def delete_path(path):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
            return True

        elif os.path.isfile(path):
            os.remove(path)
            return True

        return False

    except:
        return False


class ShareFile:
    def __init__(self, server: ServerSocket):
        self.server = server
        pythoncom.CoInitialize()

    def start_listening(self, s):
        if type(s) == type([]):
            if s[0] == "OPEN":
                files = get_files(s[1])
                self.server.send_obj(files)

            elif s[0] == "DELETE":
                path = s[1]
                if delete_path(path):
                    self.server.send_obj(["SUCCESS"])

                else:
                    self.server.send_obj(["FAIL"])

            elif s[0] == "RECEIVE":
                s = self.server.receive_item(s[1])
                if s is None:
                    self.server.send_obj(["SUCCESS"])

                else:
                    self.server.send_obj([s])

            elif s[0] == "SEND":
                self.server.send_item(s[1], s[2])

            elif s[0] == "COPY":
                s = copy_file(s[1], s[2])
                if s:
                    self.server.send_obj(["SUCCESS"])

                else:
                    self.server.send_obj(["FAIL"])

            else:
                return False

            return True

        else:
            return False
