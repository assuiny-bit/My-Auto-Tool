import tkinter as tk
import time
import threading
import ctypes
import random
import sys
import pyautogui
import os

# =================================================================
# C 強化版：完整自動化流程 (含圖像搜尋與 Alt+右鍵 20次)
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
KEYEVENTF_EXTENDEDKEY = 0x0001

# 定義掃描碼 (Scan Codes)
SCAN_X = 0x2D      # X 鍵
SCAN_9 = 0x0A      # 數字 9
SCAN_DOWN = 0x50   # 方向鍵下
SCAN_ENTER = 0x1C  # Enter 鍵
SCAN_I = 0x17      # I 鍵
SCAN_ALT = 0x38    # 左 Alt 鍵

# 滑鼠常數
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010

try:
    win32u = ctypes.WinDLL("win32u.dll", use_last_error=True)
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

def right_click():
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
    time.sleep(random.uniform(0.05, 0.1))
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)

user32 = ctypes.windll.user32
SetCursorPos = user32.SetCursorPos

class CustomApp:
    def __init__(self, root):
        self.root = root
        self.root.title("進階按鍵助手 (Alt+右鍵版)")
        self.root.geometry("400x380")
        self.root.attributes("-topmost", True)
        self.is_running = False
        
        tk.Label(root, text="自動化流程 (含 Alt+右鍵 20次)", font=("Arial", 11, "bold")).pack(pady=10)
        self.status_label = tk.Label(root, text="狀態: 待機中", font=("Arial", 11))
        self.status_label.pack(pady=20)
        self.start_btn = tk.Button(root, text="開始執行", command=self.start, width=20, height=2, bg="#FF5722", fg="white")
        self.start_btn.pack(pady=5)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.start_btn.config(state="disabled")
            threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        # 1-6 步: 之前的流程
        for i in range(3, 0, -1):
            self.status_label.config(text=f"請切換視窗... {i}")
            time.sleep(1)
        
        self.status_label.config(text="執行: X -> 9 -> ↓ -> Enter*2 -> I")
        send_key(SCAN_X); time.sleep(0.1); send_key(SCAN_X, True); time.sleep(1.0)
        send_key(SCAN_9); time.sleep(0.1); send_key(SCAN_9, True); time.sleep(0.5)
        send_key(SCAN_DOWN, False, True); time.sleep(0.1); send_key(SCAN_DOWN, True, True); time.sleep(0.5)
        for _ in range(2):
            send_key(SCAN_ENTER); time.sleep(0.1); send_key(SCAN_ENTER, True); time.sleep(0.7)
        send_key(SCAN_I); time.sleep(0.1); send_key(SCAN_I, True); time.sleep(0.5)

        # 7. 搜尋圖片並移動滑鼠
        self.status_label.config(text="執行: 搜尋圖片 '01.png'...")
        try:
            base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(".")
            image_path = os.path.join(base_path, "01.png")
            location = pyautogui.locateOnScreen(image_path, confidence=0.9)
            if location:
                target_x = (location.left + location.width // 2) + 150
                target_y = (location.top + location.height // 2) - 150
                SetCursorPos(target_x, target_y)
                time.sleep(0.5)
            else:
                self.status_label.config(text="未找到圖片，跳過滑鼠移動")
        except: pass

        # 8. 壓住 Alt 並點擊右鍵 20 次
        self.status_label.config(text="執行: 壓住 Alt + 右鍵 20 次")
        send_key(SCAN_ALT, False) # 壓住 Alt
        time.sleep(0.2)
        
        for k in range(20):
            if not self.is_running: break
            self.status_label.config(text=f"右鍵點擊: {k+1}/20")
            right_click()
            time.sleep(0.6) # 每次間隔 0.6 秒
            
        send_key(SCAN_ALT, True) # 放開 Alt
        
        self.status_label.config(text="狀態: 執行完畢")
        self.is_running = False
        self.start_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = CustomApp(root)
    root.mainloop()
