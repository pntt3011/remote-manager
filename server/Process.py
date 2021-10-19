import subprocess
import win32process
import win32api
import os


class Process:
    def __init__(self, server):
        self.server = server
        self.st_info = subprocess.STARTUPINFO()
        self.st_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    def start_listening(self):
        dict = {
            "XEM": self.list_process,
            "KILL": self.kill_process,
            "START": self.start_process,
        }

        while True:
            print("PROCESS:")
            s = self.server.receive_signal()

            if s in dict:
                dict[s]()
            elif s == "QUIT":
                break

    def list_process(self):
        proc = str(
            subprocess.check_output(
                "wmic process get ProcessId,Name,ThreadCount",
                startupinfo=self.st_info,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )
        ).split("\\r\\r\\n")
        processList = [
            tuple(x.split())
            for x in proc
            if len(x.split()) == 3 and x.split()[1].isnumeric()
        ]
        self.server.send_obj(processList)

    def kill_process(self):
        while True:
            print("KILL_PROCESS:")
            s = self.server.receive_signal()

            if s == "KILLID":

                # Get running processes
                pids = self.get_process()
                pid = self.server.receive_signal()

                # Invalid pid
                if pid not in pids:
                    print("Invalid process")
                    self.server.send_signal("Invalid process")
                    continue

                # If valid, kill
                self.kill_process_pid(pid)

            elif s == "QUIT":
                break

    def kill_process_pid(self, pid):
        try:
            handle = win32api.OpenProcess(1, 0, int(pid))
            win32process.TerminateProcess(handle, -1)
            print("Killed:", pid)
            self.server.send_signal("Killed")

        except:
            print("Error")
            self.server.send_signal("Error")

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
            s = self.server.receive_signal()

            if s == "STARTID":
                name = self.server.receive_signal() + ".exe"

                try:
                    os.startfile(name)
                    self.server.send_signal("Process started")
                    print("Process started")

                except:
                    self.server.send_signal("Error")
                    print("Error")

            elif s == "QUIT":
                break
