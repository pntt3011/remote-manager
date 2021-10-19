import subprocess


class OS:
    def __init__(self):
        self.st_info = subprocess.STARTUPINFO()
        self.st_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

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
