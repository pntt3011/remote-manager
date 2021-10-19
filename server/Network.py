import psutil


class Network:
    def __init__(self, server):
        self.server = server

    def start_listening(self, s):
        dict = {"MAC_ADDRESS": self.mac_address}

        if s in dict:
            dict[s]()
            return True

        return False

    def mac_address(self):
        print("GET MAC:")
        mac = list(self.get_mac_address())
        self.server.send_obj(mac)

    def get_mac_address(self):
        for interface, snics in psutil.net_if_addrs().items():
            for snic in snics:
                if snic.family == -1:
                    mac = snic.address
                if snic.family == 2:
                    yield (interface, mac)
