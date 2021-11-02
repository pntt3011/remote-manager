import cv2
import pyautogui
import numpy as np
import socket
import pickle
import struct
import threading
from mss import mss

class ScreenShare:
    def __init__(self, server, host, port, x_res=1000, y_res=560):
        self.server = server
        self.host = host
        self.port = port
        self.x_res = x_res
        self.y_res = y_res
        self.running = False
        self.encoding_parameters = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        self.w, self.h = pyautogui.size()

    def set_resolution(self):
        x, y = 0, 0
        x, y = self.server.receive_obj()
        self.x_res = int(x)
        self.y_res = int(y)
        print(x, y)
        # self.server.send_obj("SUCCESS")

    def client_streaming(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

        with mss() as sct:
            monitor = {"top": 0, "left": 0, "width": self.w, "height": self.h}

            while self.running:
                self.frame = sct.grab(monitor)
                self.frame = cv2.UMat(np.array(self.frame))
                self.frame = cv2.resize(self.frame, (self.x_res, self.y_res))
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)
                _, self.frame = cv2.imencode(".jpg", self.frame, self.encoding_parameters)
                data = pickle.dumps(self.frame, 0)
                size = len(data)

                try:
                    self.client_socket.sendall(struct.pack(">L", size) + data)
                except:
                    self.running = False

    def start_stream(self):
        if not self.running:
            self.running = True
            self.thread= threading.Thread(target=self.client_streaming)
            self.thread.start()

    def stop_stream(self):
        if self.running:
            self.running = False
            self.thread.join()
            self.client_socket.close()
