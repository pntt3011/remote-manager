import winreg
import subprocess
import os
import sys


class Registry:
    def __init__(self, server):
        self.server = server
        self.st_info = subprocess.STARTUPINFO()
        self.st_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    def start_listening(self, s):
        dict = {"REG": self.reg_registry, "SEND": self.send_registry}

        if s in dict:
            dict[s]()
            return True

        return False

    def reg_registry(self):
        print("REG_REGISTRY")

        file_name = "fileReg.reg"
        path = os.path.dirname(os.path.realpath(sys.argv[0])) + "\\" + file_name

        s = self.server.receive_obj()

        try:
            with open(path, "w") as f:
                f.write(s)

            out = str(
                subprocess.check_output(
                    'reg import "' + path + '"',
                    startupinfo=self.st_info,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                )
            )

            if "ERROR" in out:
                print("Failed")
                self.server.send_signal("Failed")

            else:
                print("Success")
                self.server.send_signal("Success")

        except:
            self.server.send_signal("Failed")
            print("Failed")

        finally:
            os.remove(path)

    def send_registry(self):
        print("SEND_REGISTRY")

        data = self.server.receive_obj()
        option = data[0]
        link = data[1]
        value_name = data[2]
        value = data[3]
        type_value = data[4]

        if "\\" not in link:
            self.server.send_signal("Error")
            return

        key = self.base_registry_key(link)
        sub_link = link[link.index("\\") + 1 :]

        if key == None:
            s = "Error"
        else:
            if option == "Create key":
                key = winreg.CreateKey(key, sub_link)
                s = "Create key successfully"

            elif option == "Delete key":
                s = self.delete_key(key, sub_link)

            elif option == "Get value":
                s = self.get_value(key, sub_link, value_name)

            elif option == "Set value":
                s = self.set_value(key, sub_link, value_name, value, type_value)

            elif option == "Delete value":
                s = self.delete_value(key, sub_link, value_name)

            else:
                s = "Error"

        self.server.send_obj(s)

    def base_registry_key(self, link):
        key = None
        dict = {
            "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
            "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
            "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
            "HKEY_USERS": winreg.HKEY_USERS,
            "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG,
        }

        if link.index("\\") >= 0:
            base = link[0 : link.index("\\")].upper()
            if base in dict:
                key = winreg.ConnectRegistry(None, dict[base])

        return key

    def get_value(self, key, link, value_name):
        try:
            key = winreg.OpenKeyEx(key, link)
        except:
            return "Error"

        try:
            data, data_type = winreg.QueryValueEx(key, value_name)
        except:
            return "Error"

        if data:
            s = ""
            if data_type == winreg.REG_BINARY or data_type == winreg.REG_MULTI_SZ:
                for i in data:
                    s += str(i) + " "

            else:
                s = str(data)

            return s

        else:
            return "Error"

    def set_value(self, key, link, value_name, value, type_value):
        try:
            key = winreg.OpenKeyEx(key, link, 0, winreg.KEY_SET_VALUE)
        except:
            return "Error"

        value, type_value = self.convert(value, type_value)
        if not value:
            return "Error"

        try:
            winreg.SetValueEx(key, value_name, 0, type_value, value)
            return "Set value successfully"
        except:
            return "Error"

    def convert(self, value, type_value):
        try:
            if type_value == "String":
                type_value = winreg.REG_SZ

            elif type_value == "Binary":
                type_value = winreg.REG_BINARY
                temp_value = value.split()
                value = bytearray()
                for i in temp_value:
                    value += bytes([int(i)])

            elif type_value == "DWORD":
                type_value = winreg.REG_DWORD
                value = int(value)

            elif type_value == "QWORD":
                type_value = winreg.REG_QWORD
                value = int(value)

            elif type_value == "Multi-String":
                type_value = winreg.REG_MULTI_SZ
                value = value.strip().split("\\0")

            elif type_value == "Expandable String":
                type_value = winreg.REG_EXPAND_SZ

            else:
                value = None

        except:
            value = None

        finally:
            return value, type_value

    def delete_key(self, key, link):
        try:
            winreg.DeleteKey(key, link)
            return "Delete key successfully"
        except:
            return "Error"

    def delete_value(self, key, link, value_name):
        try:
            key = winreg.OpenKeyEx(key, link, 0, winreg.KEY_SET_VALUE)
        except:
            return "Error"

        try:
            winreg.DeleteValue(key, value_name)
            return "Delete value successfuly"
        except:
            return "Error"
