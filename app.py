import tkinter as tk
import time
import threading
import ctypes
import random
import sys
import pyautogui
import os

# =================================================================
# C 強化版 V2.6：完整終極流程 (1-13 步)
# =================================================================

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort), ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong), ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]
class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong), ("wParamL", ctypes.c_ushort), ("wParamH", ctypes.c_ushort)]
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long), ("mouseData", ctypes.c_ulong), ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong), ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]
class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]
class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("union", INPUT_UNION)]

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_EXTENDEDKEY = 0x0001

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010

# 掃描碼定義
SCAN_ESC = 0x01
SCAN_X = 0x2D; SCAN_9 = 0x0A; SCAN_DOWN = 0x50; SCAN_ENTER = 0x1C; SCAN_I = 0x17; SCAN_ALT = 0x38

try:
    win32u = ctypes.WinDLL("win32u.dll", use_last_error=True)
    NtUserSendInput = win32u.NtUserSendInput
    NtUserSendInput.argtypes = (ctypes.c_ulong, ctypes.POINTER(INPUT), ctypes.c_int)
    NtUserSendInput.restype = ctypes.c_ulong
except:
    NtUserSendInput = None

user32 = ctypes.windll.user32

def send_input(ii):
    if NtUserSendInput:
        NtUserSendInput(1, ctypes.byref(ii), ctypes.sizeof(ii))
    else:
        user32.SendInput(1, ctypes.byref(ii), ctypes.sizeof(ii))

def move_mouse_to(x, y):
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    nx = int(x * 65536 / width)
    ny = int(y * 65536 / height)
    mi = MOUSEINPUT(dx=nx, dy=ny, mouseData=0, dwFlags=MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, time=0, dwExtraInfo=None)
    send_input(INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=mi)))

def mouse_left_click():
    mi_down = MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=MOUSEEVENTF_LEFTDOWN, time=0, dwExtraInfo=None)
    send_input(INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=mi_down)))
    time.sleep(random.uniform(0.05, 0.1))
    mi_up = MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=MOUSEEVENTF_LEFTUP, time=0, dwExtraInfo=None)
    send_input(INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=mi_up)))

def mouse_right_click():
    mi_down = MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=MOUSEEVENTF_RIGHTDOWN, time=0, dwExtraInfo=None)
    send_input(INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=mi_down)))
    time.sleep(random.uniform(0.05, 0.1))
    mi_up = MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=MOUSEEVENTF_RIGHTUP, time=0, dwExtraInfo=None)
    send_input(INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=mi_up)))

def send_key(scancode, is_up=False, is_extended=False):
    flags = KEYEVENTF_SCANCODE
    if is_up: flags |= KEYEVENTF_KEYUP
    if is_extended: flags |= KEYEVENTF_EXTENDEDKEY
    ki = KEYBDINPUT(wVk=0, wScan=scancode, dwFlags=flags, time=0, dwExtraInfo=None)
    send_input(INPUT(type=INPUT_KEYBOARD, union=INPUT_UNION(ki=ki)))

class CustomApp:
    def __init__(self, root):
        self.root = root
        self.root.title("終極按鍵助手 V2.6")
        self.root.geometry("400x420")
        self.root.attributes("-topmost", True)
        self.is_running = False
        
        tk.Label(root, text="終極全流程 (1-13 步)", font=("Arial", 12, "bold")).pack(pady=10)
        self.status_label = tk.Label(root, text="狀態: 待機中", font=("Arial", 11), fg="blue")
        self.status_label.pack(pady=20)
        self.start_btn = tk.Button(root, text="開始全流程", command=self.start, width=20, height=2, bg="#4CAF50", fg="white")
        self.start_btn.pack(pady=5)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.start_btn.config(state="disabled")
            threading.Thread(target=self.run, daemon=True).start()

    def find_and_click_with_offset(self, img_name, offset_x=0, offset_y=0, click_center=True):
        try:
            base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(".")
            image_path = os.path.join(base_path, img_name)
            location = pyautogui.locateOnScreen(image_path, confidence=0.85)
            if location:
                cx = location.left + location.width // 2
                cy = location.top + location.height // 2
                if click_center:
                    move_mouse_to(cx, cy)
                    time.sleep(0.2)
                    mouse_left_click()
                    time.sleep(0.5)
                
                target_x = cx + offset_x
                target_y = cy + offset_y
                move_mouse_to(target_x, target_y)
                time.sleep(0.5)
                return True
            return False
        except: return False

    def run(self):
        # 1. 倒數 3 秒
        for i in range(3, 0, -1):
            self.status_label.config(text=f"請切換視窗... {i}")
            time.sleep(1)
        
        # 2-6 步: 基礎按鍵
        self.status_label.config(text="執行: 步驟 2-6 (按鍵序列)")
        send_key(SCAN_X); time.sleep(0.1); send_key(SCAN_X, True); time.sleep(1.0)
        send_key(SCAN_9); time.sleep(0.1); send_key(SCAN_9, True); time.sleep(0.5)
        send_key(SCAN_DOWN, False, True); time.sleep(0.1); send_key(SCAN_DOWN, True, True); time.sleep(0.5)
        for _ in range(2):
            send_key(SCAN_ENTER); time.sleep(0.1); send_key(SCAN_ENTER, True); time.sleep(0.7)
        send_key(SCAN_I); time.sleep(0.1); send_key(SCAN_I, True); time.sleep(0.5)

        # 7-8 步: 搜尋 01.png 並偏移 + Alt右鍵 20次
        self.status_label.config(text="執行: 步驟 7-8 (01.png 偏移)")
        if self.find_and_click_with_offset("01.png", 28, -30):
            send_key(SCAN_ALT, False); time.sleep(0.2)
            for k in range(20):
                if not self.is_running: break
                self.status_label.config(text=f"右鍵點擊 (01): {k+1}/20")
                mouse_right_click(); time.sleep(0.6)
            send_key(SCAN_ALT, True); time.sleep(0.5)

        # 9-10 步: 搜尋 02.png 並偏移 + Alt右鍵 6次
        self.status_label.config(text="執行: 步驟 9-10 (02.png 偏移)")
        if self.find_and_click_with_offset("02.png", 28, -60):
            send_key(SCAN_ALT, False); time.sleep(0.2)
            for k in range(6):
                if not self.is_running: break
                self.status_label.config(text=f"右鍵點擊 (02): {k+1}/6")
                mouse_right_click(); time.sleep(0.6)
            send_key(SCAN_ALT, True); time.sleep(0.5)

        # 11 步: 按下 Esc
        self.status_label.config(text="執行: 步驟 11 (Esc)")
        send_key(SCAN_ESC); time.sleep(0.1); send_key(SCAN_ESC, True); time.sleep(0.5)

        # 12 步: 搜尋 ca2.png 並點擊
        self.status_label.config(text="執行: 步驟 12 (ca2.png)")
        self.find_and_click_with_offset("ca2.png", 0, 0, click_center=True); time.sleep(0.5)

        # 13 步: 按下 X
        self.status_label.config(text="執行: 步驟 13 (X)")
        send_key(SCAN_X); time.sleep(0.1); send_key(SCAN_X, True)

        self.status_label.config(text="狀態: 全流程執行完畢")
        self.is_running = False
        self.start_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = CustomApp(root)
    root.mainloop()
