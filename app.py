import tkinter as tk
import time
import threading
import ctypes
import random
import sys

# =================================================================
# C 強化版：完整自動化流程 (X -> 9 -> Down -> Enter*2 -> I)
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

INPUT_KEYBOARD = 1
KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_EXTENDEDKEY = 0x0001 # 用於方向鍵等擴展按鍵

# 定義掃描碼 (Scan Codes)
SCAN_X = 0x2D      # X 鍵
SCAN_9 = 0x0A      # 字母區上方的數字 9
SCAN_DOWN = 0x50   # 方向鍵下
SCAN_ENTER = 0x1C  # Enter 鍵
SCAN_I = 0x17      # I 鍵

try:
    win32u = ctypes.WinDLL('win32u.dll', use_last_error=True)
    NtUserSendInput = win32u.NtUserSendInput
    NtUserSendInput.argtypes = (ctypes.c_ulong, ctypes.POINTER(INPUT), ctypes.c_int)
    NtUserSendInput.restype = ctypes.c_ulong
except:
    NtUserSendInput = None

def send_key(scancode, is_up=False, is_extended=False):
    flags = KEYEVENTF_SCANCODE
    if is_up: flags |= KEYEVENTF_KEYUP
    if is_extended: flags |= KEYEVENTF_EXTENDEDKEY
    
    ki = KEYBDINPUT(wVk=0, wScan=scancode, dwFlags=flags, time=0, dwExtraInfo=None)
    ii = INPUT(type=INPUT_KEYBOARD, union=INPUT_UNION(ki=ki))
    if NtUserSendInput:
        NtUserSendInput(1, ctypes.byref(ii), ctypes.sizeof(ii))
    else:
        ctypes.windll.user32.SendInput(1, ctypes.byref(ii), ctypes.sizeof(ii))

class CustomApp:
    def __init__(self, root):
        self.root = root
        self.root.title("進階按鍵助手 (完整流程)")
        self.root.geometry("350x300")
        self.root.attributes("-topmost", True)
        self.is_running = False
        
        tk.Label(root, text="自動化流程 (X -> 9 -> ↓ -> ↩*2 -> I)", font=("Arial", 11, "bold")).pack(pady=10)
        self.status_label = tk.Label(root, text="狀態: 待機中", font=("Arial", 11))
        self.status_label.pack(pady=20)
        self.start_btn = tk.Button(root, text="開始執行", command=self.start, width=20, height=2, bg="#E91E63", fg="white")
        self.start_btn.pack(pady=5)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.start_btn.config(state="disabled")
            threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        # 1. 倒數 3 秒
        for i in range(3, 0, -1):
            self.status_label.config(text=f"請切換視窗... {i}")
            time.sleep(1)
        
        # 2. 按下 X 並等待 1 秒
        self.status_label.config(text="執行: 按下 X")
        send_key(SCAN_X, False); time.sleep(0.1); send_key(SCAN_X, True)
        time.sleep(1.0)
        
        # 3. 按下數字 9
        self.status_label.config(text="執行: 按下 9")
        send_key(SCAN_9, False); time.sleep(0.1); send_key(SCAN_9, True)
        time.sleep(0.5)
        
        # 4. 按下方向鍵下
        self.status_label.config(text="執行: 按下方向鍵下")
        send_key(SCAN_DOWN, False, is_extended=True); time.sleep(0.1); send_key(SCAN_DOWN, True, is_extended=True)
        time.sleep(0.5)
        
        # 5. 按下 2 次 Enter，間隔 0.7 秒
        for j in range(2):
            self.status_label.config(text=f"執行: 按下 Enter (第 {j+1} 次)")
            send_key(SCAN_ENTER, False); time.sleep(0.1); send_key(SCAN_ENTER, True)
            if j == 0: time.sleep(0.7)
        time.sleep(0.5)
        
        # 6. 按下 I 鍵
        self.status_label.config(text="執行: 按下 I 鍵")
        send_key(SCAN_I, False); time.sleep(0.1); send_key(SCAN_I, True)
        
        self.status_label.config(text="狀態: 執行完畢")
        self.is_running = False
        self.start_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = CustomApp(root)
    root.mainloop()
