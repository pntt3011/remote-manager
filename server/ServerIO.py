from pynput.keyboard import Key, Controller
from ServerSocket import ServerSocket
import pyautogui
import socket

HOST = ""
PORT = 5656
ADDR = (HOST, PORT)

key_map = {
    'Escape': Key.esc,
    'F1': Key.f1,
    'F2': Key.f2,
    'F3': Key.f3,
    'F4': Key.f4,
    'F5': Key.f5,
    'F6': Key.f6,
    'F7': Key.f7,
    'F8': Key.f8,
    'F9': Key.f9,
    'F10': Key.f10,
    'F11': Key.f11,
    'F12': Key.f12,
    'Home': Key.home,
    'End': Key.end,
    'Insert': Key.insert,
    'Delete': Key.delete,
    'quoteleft': '`',
    '1': '1',
    '2': '2',
    '3': '3',
    '4': '4',
    '5': '5',
    '6': '6',
    '7': '7',
    '8': '8',
    '9': '9',
    '0': '0',
    'minus': '-',
    'equal': '=',
    'BackSpace': Key.backspace,
    'Tab': Key.tab,
    'bracketleft': '[',
    'bracketright': ']',
    'backslash': '\\',
    'Caps_Lock': Key.caps_lock,
    'Q': 'q',
    'W': 'w',
    'E': 'e',
    'R': 'r',
    'T': 't',
    'Y': 'y',
    'U': 'u',
    'I': 'i',
    'O': 'o',
    'P': 'p',
    'A': 'a',
    'S': 's',
    'D': 'd',
    'F': 'f',
    'G': 'g',
    'H': 'h',
    'J': 'j',
    'K': 'k',
    'L': 'l',
    'Z': 'z',
    'X': 'x',
    'C': 'c',
    'V': 'v',
    'B': 'b',
    'N': 'n',
    'M': 'm',
    'semicolon': ';',
    'quoteright': '\'',
    'Return': Key.enter,
    'q': 'q',
    'w': 'w',
    'e': 'e',
    'r': 'r',
    't': 't',
    'y': 'y',
    'u': 'u',
    'i': 'i',
    'o': 'o',
    'p': 'p',
    'a': 'a',
    's': 's',
    'd': 'd',
    'f': 'f',
    'g': 'g',
    'h': 'h',
    'j': 'j',
    'k': 'k',
    'l': 'l',
    'z': 'z',
    'x': 'x',
    'c': 'c',
    'v': 'v',
    'b': 'b',
    'n': 'n',
    'm': 'm',
    'Shift_L': Key.shift,
    'comma': ',',
    'period': '.',
    'slash': '/',
    'Shift_R': Key.shift_r,
    'Control_L': Key.ctrl_l,
    'Win_L': Key.cmd,
    'Alt_L': Key.alt_l,
    'space': Key.space,
    'Alt_R': Key.alt_gr,
    'Control_R': Key.ctrl_r,
    'Prior': Key.page_up,
    'Next': Key.page_down,
    'Up': Key.up,
    'Left': Key.left,
    'Down': Key.down,
    'Right': Key.right,
    'exclam': '!',
    'at': '@',
    'numbersign': '#',
    'dollar': '$',
    'percent': '%',
    'asciicircum': '^',
    'ampersand': '&',
    'asterisk': '*',
    'parenleft': '(',
    'parenright': ')',
    'underscore': '_',
    'plus': '+',
    'braceleft': '{',
    'braceright': '}',
    'bar': '|',
    'colon': ':',
    'quotedbl': '"',
    'less': '<',
    'greater': '>',
    'question': '?',
}


class ServerIO:
    def __init__(self):
        self.keyboard = Controller()
        self.w, self.h = pyautogui.size()
        self.dict = {
            "MOUSE_MOVE": self.mouse_move,
            "KEY_PRESS": lambda s: self.keyboard.press(key_map[s]),
            "KEY_RELEASE": lambda s: self.keyboard.release(key_map[s]),
            "MOUSE_UP": lambda s: pyautogui.mouseUp(button=s),
            "MOUSE_DOWN": lambda s: pyautogui.mouseDown(button=s)
        }
        self.open_server()

    def open_server(self):
        self.server = ServerSocket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(ADDR)
        self.server.listen(1)

    def start_listening(self):
        try:
            self.server.accept()
            print("Accepted")
        finally:
            self.flag = True

            while self.flag:
                s = self.server.receive_obj()

                if s == "QUIT":
                    break

                if s[0] in self.dict:
                    print(s[0])
                    self.dict[s[0]](s[1])

    def mouse_move(self, s):
        x = int(float(s[0]) * self.w)
        y = int(float(s[1]) * self.h)
        pyautogui.moveTo(x, y)

    def stop(self):
        self.flag = False

    def close(self):
        self.stop()
        self.server.close()
