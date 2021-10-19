from ScreenShare import ScreenShare
import threading


class Screen:
    def __init__(self, server):
        self.receiver = ScreenShare('127.0.0.1', 9999)
        self.server = server

    def start_recording(self):
        threading.Thread(target=self.receiver.start_stream,
                         daemon=True).start()
        while True:
            print("TAKEPIC:")
            s = self.server.receive_signal()

            if s == "QUIT":
                break

        self.receiver.stop_stream()
