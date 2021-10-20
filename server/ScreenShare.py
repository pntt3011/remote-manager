import cv2
import pyautogui
import numpy as np
import socket
import pickle
import struct
import threading

class ScreenShare:
    def __init__(self, server, host, port, x_res=1000, y_res=560):
        self.server = server
        self.host = host
        self.port = port
        self.x_res = x_res
        self.y_res = y_res
        self.running = False
        self.encoding_parameters = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

    def set_resolution(self):
        x, y = 0, 0
        x, y = self.server.receive_obj()
        self.x_res = int(x)
        self.y_res = int(y)
        print(x, y)
        # self.server.send_signal("SUCCESS")

    def get_frame(self):
        screen = pyautogui.screenshot()
        frame = cv2.UMat(np.array(screen))
        frame = cv2.resize(frame, (self.x_res, self.y_res))
        return frame

    def client_streaming(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        # print(self.host, self.port)
        # print(self.running)
        while self.running:
            frame = self.get_frame()
            _, frame = cv2.imencode(".jpg", frame, self.encoding_parameters)
            data = pickle.dumps(frame, 0)
            size = len(data)

            try:
                self.client_socket.sendall(struct.pack(">L", size) + data)
            except:
                self.running = False

    def start_stream(self):
        print('cac')
        if not self.running:
            self.running = True
            threading.Thread(target=self.client_streaming, daemon=True).start()

    def stop_stream(self):
        if self.running:
            self.running = False
            self.client_socket.close()
