from ScreenShare import ScreenShare
import threading


class Screen:
    def __init__(self, server):
        self.receiver = ScreenShare("127.0.0.1", 9999)
        self.server = server

    def start_listening(self, s):
        dict = {
            "START_CAPTURE": self.receiver.start_stream,
            "STOP_CAPTURE": self.receiver.stop_stream,
        }

        if s in dict:
            dict[s]()
            return True

        return False
