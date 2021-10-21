import subprocess
import win32process
import win32api
import os


class Process:
    def __init__(self, server):
        self.server = server
        self.st_info = subprocess.STARTUPINFO()
        self.st_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    def start_listening(self, s):
        dict = {
            "XEM_PROCESS": self.list_process,
            "KILL_PROCESS": self.kill_process,
            "START_PROCESS": self.start_process,
        }

        if s in dict:
            dict[s]()
            return True

        return False

    def list_process(self):
        proc = str(
            subprocess.check_output(
                "wmic process get ProcessId,Name,ThreadCount",
                startupinfo=self.st_info,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )
        ).split("\\r\\r\\n")
        process_list = [
            tuple(x.split())
            for x in proc
            if len(x.split()) == 3 and x.split()[1].isnumeric()
        ]
        self.server.send_obj(process_list)

    def kill_process(self):
        # Get running processes
        pids = self.get_process()
        pid = self.server.receive_obj()

        # Invalid pid
        if pid not in pids:
            print("Invalid process")
            self.server.send_obj("Invalid process")
            return

        # If valid, kill
        self.kill_process_pid(pid)

    def kill_process_pid(self, pid):
        try:
            handle = win32api.OpenProcess(1, 0, int(pid))
            win32process.TerminateProcess(handle, -1)
            print("Killed:", pid)
            self.server.send_obj("Killed")

        except:
            print("Error")
            self.server.send_obj("Error")

    def get_process(self):
        res = []
        proc = str(
            subprocess.check_output(
                "wmic process get ProcessId",
                startupinfo=self.st_info,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )
        ).split("\\r\\r\\n")
        for i in proc:
            data = i.split()
            if len(data) == 1 and data[0].isnumeric():
                res.append(data[0])
        return res

    def start_process(self):
        while True:
            print("START_PROCESS:")
            s = self.server.receive_obj()

            if s == "STARTID":
                name = self.server.receive_obj() + ".exe"

                try:
                    os.startfile(name)
                    self.server.send_obj("Process started")
                    print("Process started")

                except:
                    self.server.send_obj("Error")
                    print("Error")

            elif s == "QUIT":
                break
