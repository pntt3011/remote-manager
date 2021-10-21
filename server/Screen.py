from ScreenShare import ScreenShare
import threading


class Screen:
    def __init__(self, server):
        self.server = server
        self.receiver = ScreenShare(self.server, "127.0.0.1", 9696)

    def start_listening(self, s):
        dict = {
            "START_CAPTURE": self.receiver.start_stream,
            "STOP_CAPTURE": self.receiver.stop_stream,
            "SET_RESOLUTION": self.receiver.set_resolution
        }

        if s in dict:
            dict[s]()
            return True

        return False
