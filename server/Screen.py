from ScreenShare import ScreenShare


class Screen:
    def __init__(self, server):
        self.server = server

    def setup_screen_share(self):
        self.receiver = ScreenShare(self.server, self.server.client_addr, 9696)

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

    def close_screen_share(self):
        self.receiver.stop_stream()
