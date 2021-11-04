from client_UI import ClientUI
from ctypes import windll
from ttkbootstrap import Style
import tkinter as tk
from path_finding import resource_path
import ctypes
import sys

def is_admin():
    try:
        return windll.shell32.IsUserAnAdmin()
    except:
        return False


if __name__ == '__main__':

    if is_admin():
        root = tk.Tk()
        scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
        root.tk.call('tk', 'scaling', scaleFactor)
        root.geometry('610x520')
        root.resizable(False, False)

        # root.state('zoomed')
        root.title('Client')
        root.iconbitmap(resource_path('res\\app_icon.ico'))

        # Set the theme
        # root.tk.call("source", os.path.dirname(
        #     os.path.realpath(__file__)) + "/sun-valley.tcl")
        # root.tk.call("set_theme", "light")
        style = Style(theme='cosmo')
        root = style.master

        client_UI = ClientUI(root)
        client_UI.pack(fill="both", expand=True)

        # Set a minsize for the window, and place it in the middle
        root.update()
        root.minsize(root.winfo_width(), root.winfo_height())
        x_cordinate = int((root.winfo_screenwidth() / 2) -
                          (root.winfo_width() / 2))
        y_cordinate = int((root.winfo_screenheight() / 2) -
                          (root.winfo_height() / 2))
        root.geometry("+{}+{}".format(x_cordinate, y_cordinate))

        root.mainloop()

    else:
        windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )