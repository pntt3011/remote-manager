from Server import Server
from KeyLogger import KeyLogger
from Window import OS
from Registry import Registry
from Screen import Screen
from Process import Process
from Application import Application
from Network import Network
from ctypes import windll

import tkinter
import threading
import sys
import socket

HOST = ""
PORT = 8080
ADDR = (HOST, PORT)


class ServerUI:
    def __init__(self):
        if self.is_admin():
            self.setup_UI()

        else:
            windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1)

    def is_admin(self):
        try:
            return windll.shell32.IsUserAnAdmin()
        except:
            return False

    def setup_UI(self):
        self.top = tkinter.Tk()
        self.top.title("Server")
        self.top.geometry("300x200")

        self.button = tkinter.Button(
            self.top, text="Mở", command=self.open_server, font=("Calibri", 20)
        )
        self.button.place(
            width=150, height=100, relx=0.5, rely=0.5, anchor=tkinter.CENTER
        )
        self.top.mainloop()

    def open_server(self):
        threading.Thread(target=self.setup_server, daemon=True).start()

    def setup_server(self):
        self.server = Server(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(ADDR)
        self.server.listen(1)

        self.key_logger = KeyLogger(self.server)
        self.os = OS()
        self.registry = Registry(self.server)
        self.screen = Screen(self.server)
        self.process = Process(self.server)
        self.application = Application(self.server)
        self.network = Network(self.server)

        self.start_listening()

    def start_listening(self):
        self.button["state"] = "disabled"
        print("Waiting for connection...")

        addr = self.server.accept()
        print("Connected by", addr)

        dict = {
            "KEYLOG": self.key_logger.start_listening,  # DONE
            "SHUTDOWN": self.os.shutdown,  # DONE
            "LOGOUT": self.os.logout,  # DONE
            "REGISTRY": self.registry.start_listening,  # DONE
            "TAKEPIC": self.screen.start_recording,  # DONE
            "PROCESS": self.process.start_listening,  # DONE
            "APPLICATION": self.application.start_listening,  # DONE
            "MAC_ADDRESS": self.network.mac_address,  # DONE
        }

        while True:
            print("MENU:")
            s = self.server.receive_signal()

            if s in dict:
                dict[s]()
            elif s == "QUIT":
                self.key_logger.stop()
                break

        self.server.close()
        self.button["state"] = "normal"

    def temp(self):
        pass


if __name__ == "__main__":
    ServerUI()
