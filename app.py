import tkinter as tk
import time
import threading
import ctypes
import random
import sys
import pyautogui
import os

# =================================================================
# C 強化版 V2.3：底層絕對座標移動 (繞過系統限制)
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
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

SCAN_X = 0x2D; SCAN_9 = 0x0A; SCAN_DOWN = 0x50; SCAN_ENTER = 0x1C; SCAN_I = 0x17; SCAN_ALT = 0x38; SCAN_ESC = 0x01

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

def mouse_right_click():
    mi_down = MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=MOUSEEVENTF_RIGHTDOWN, time=0, dwExtraInfo=None)
    send_input(INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=mi_down)))
    time.sleep(random.uniform(0.05, 0.1))
    mi_up = MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=MOUSEEVENTF_RIGHTUP, time=0, dwExtraInfo=None)
    send_input(INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=mi_up)))

def mouse_left_click():
    mi_down = MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=MOUSEEVENTF_LEFTDOWN, time=0, dwExtraInfo=None)
    send_input(INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=mi_down)))
    time.sleep(random.uniform(0.05, 0.1))
    mi_up = MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=MOUSEEVENTF_LEFTUP, time=0, dwExtraInfo=None)
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
        self.root.title("自動化測試 V2.7")
        self.root.geometry("400x380")
        self.root.attributes("-topmost", True)
        self.is_running = False
        
        tk.Label(root, text="自動化流程 (步驟 1-13)", font=("Arial", 11, "bold")).pack(pady=10)
        self.status_label = tk.Label(root, text="狀態: 待機中", font=("Arial", 11))
        self.status_label.pack(pady=20)
        self.start_btn = tk.Button(root, text="開始執行", command=self.start, width=20, height=2, bg="#4CAF50", fg="white")
        self.start_btn.pack(pady=5)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.start_btn.config(state="disabled")
            threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(".")
        
        for i in range(3, 0, -1):
            self.status_label.config(text=f"請切換視窗... {i}")
            time.sleep(1)
        
        # 1-6 步: 鍵盤流程
        self.status_label.config(text="執行: 基礎按鍵序列...")
        send_key(SCAN_X); time.sleep(0.1); send_key(SCAN_X, True); time.sleep(1.0)
        send_key(SCAN_9); time.sleep(0.1); send_key(SCAN_9, True); time.sleep(0.5)
        send_key(SCAN_DOWN, False, True); time.sleep(0.1); send_key(SCAN_DOWN, True, True); time.sleep(0.5)
        for _ in range(2):
            send_key(SCAN_ENTER); time.sleep(0.1); send_key(SCAN_ENTER, True); time.sleep(0.7)
        send_key(SCAN_I); time.sleep(0.1); send_key(SCAN_I, True); time.sleep(0.5)

        # 7. 搜尋 01.png 並定位基準點
        self.status_label.config(text="正在搜尋 '01.png'...")
        base_x, base_y = 0, 0
        try:
            image_path_01 = os.path.join(base_path, "01.png")
            location_01 = pyautogui.locateOnScreen(image_path_01, confidence=0.8)
            if location_01:
                base_x = (location_01.left + location_01.width // 2) + 32
                base_y = (location_01.top + location_01.height // 2) - 30
                self.status_label.config(text=f"定位 01 成功! 移動至 ({base_x}, {base_y})")
                move_mouse_to(base_x, base_y)
                time.sleep(0.8)
            else:
                self.status_label.config(text="未找到圖片 '01.png'")
                pos = pyautogui.position()
                base_x, base_y = pos.x, pos.y
                time.sleep(1)
        except: pass

        # 8. 壓住 Alt 並點擊右鍵 20 次
        self.status_label.config(text="執行: Alt + 右鍵 20 次")
        send_key(SCAN_ALT, False)
        time.sleep(0.3)
        for k in range(20):
            if not self.is_running: break
            mouse_right_click()
            time.sleep(0.6)
        send_key(SCAN_ALT, True)
        time.sleep(0.5)

        # 9. 相對偏移點擊 (左 32, 下 60)
        self.status_label.config(text="執行: 偏移點擊 (左 32, 下 60)")
        curr_x = base_x - 32
        curr_y = base_y + 60
        move_mouse_to(curr_x, curr_y)
        time.sleep(0.5)
        mouse_left_click()
        time.sleep(1.0)

        # 10. 回到基準點, Alt + 右鍵 10 次
        self.status_label.config(text="執行: 回位 Alt + 右鍵 10 次")
        move_mouse_to(base_x, base_y)
        time.sleep(0.5)
        send_key(SCAN_ALT, False)
        time.sleep(0.3)
        for k in range(10):
            if not self.is_running: break
            mouse_right_click()
            time.sleep(0.5)
        send_key(SCAN_ALT, True)
        time.sleep(0.5)

        # 11. 相對偏移點擊 (左 32, 下 30) + ESC
        self.status_label.config(text="執行: 偏移點擊 + ESC")
        move_mouse_to(base_x - 32, base_y + 30)
        time.sleep(0.5)
        mouse_left_click()
        time.sleep(0.5)
        send_key(SCAN_ESC); time.sleep(0.1); send_key(SCAN_ESC, True)
        
        # --- 步驟 12 之前的關鍵等待 ---
        self.status_label.config(text="等待介面穩定 (2秒)...")
        time.sleep(2.0)

        # 12. 搜尋 'CLOSS.png' 並執行兩次向右偏移點擊
        self.status_label.config(text="正在搜尋 'CLOSS.png' (關閉)...")
        try:
            image_path_closs = os.path.join(base_path, "CLOSS.png")
            location_closs = pyautogui.locateOnScreen(image_path_closs, confidence=0.8)
            if location_closs:
                # 儲存中心座標
                closs_x = location_closs.left + location_closs.width // 2
                closs_y = location_closs.top + location_closs.height // 2
                
                self.status_label.config(text="定位 CLOSS 成功! 執行兩次偏移點擊")
                
                # 第一次向右偏移 20 (0.2)
                move_mouse_to(closs_x + 20, closs_y)
                time.sleep(0.3)
                mouse_left_click()
                time.sleep(0.5)
                
                # 第二次再向右偏移 20 (相對於中心點總共偏移 40)
                move_mouse_to(closs_x + 40, closs_y)
                time.sleep(0.3)
                mouse_left_click()
                
                self.status_label.config(text="點擊完成，延遲 1 秒...")
                time.sleep(1.0)
            else:
                self.status_label.config(text="未找到圖片 'CLOSS.png'")
                time.sleep(1.5)
        except: pass

        # 13. 按 X 鍵
        self.status_label.config(text="執行: 按 X 鍵")
        send_key(SCAN_X); time.sleep(0.1); send_key(SCAN_X, True)
        
        self.status_label.config(text="狀態: 執行完畢")
        self.is_running = False
        self.start_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = CustomApp(root)
    root.mainloop()
