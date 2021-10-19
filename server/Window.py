import subprocess


class OS:
    def __init__(self):
        self.st_info = subprocess.STARTUPINFO()
        self.st_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    def start_listening(self, s):
        dict = {"SHUTDOWN": self.shutdown, "LOGOUT": self.logout}

        if s in dict:
            dict[s]()
            return True

        return False

    def shutdown(self):
        subprocess.call(
            "shutdown -s",
            startupinfo=self.st_info,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )

    def logout(self):
        subprocess.call(
            "shutdown -L",
            startupinfo=self.st_info,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
