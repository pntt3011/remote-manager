from Process import Process
import subprocess
import win32process
import win32gui


class Application(Process):
    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)

    def start_listening(self, s):
        dict = {
            "XEM_APP": self.list_application,
            "KILL_APP": self.kill_application,
            "START_APP": self.start_process,
        }

        if s in dict:
            dict[s]()
            return True

        return False

    def list_application(self):
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

        app_pid = self.get_application()
        apps = [i for i in process_list if i[1] in app_pid]
        self.server.send_obj(apps)

    def kill_application(self):
        while True:
            print("KILL_APPLICATION:")
            s = self.server.receive_signal()

            if s == "KILLID":

                # Get running processes
                print("ID:")
                pids = self.get_application()
                pid = self.server.receive_signal()

                # Invalid pid
                if pid not in pids:
                    print("Invalid application")
                    self.server.send_signal("Invalid application")
                    continue

                # If valid, kill
                self.kill_process_pid(pid)

            elif s == "QUIT":
                break

    def get_application(self):
        def callback(hwnd, apps):
            if (
                win32gui.IsWindowVisible(hwnd)
                and win32gui.IsWindowEnabled(hwnd)
                and win32gui.GetWindowText(hwnd) != ""
            ):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                apps.append(str(found_pid))
            return True

        apps = []
        win32gui.EnumWindows(callback, apps)
        return set(apps)
