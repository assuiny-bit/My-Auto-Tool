import tkinter as tk
import time
import threading
import ctypes
import random
import sys
import pyautogui
import os

# =================================================================
# C 強化版 V3.3：重構步驟 12 (仿照步驟 7)、停止功能與 4小時循環
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
        self.root.title("自動化循環 V3.3")
        self.root.geometry("400x450")
        self.root.attributes("-topmost", True)
        self.is_running = False
        self.stop_requested = False
        self.cycle_count = 0
        
        tk.Label(root, text="自動化流程 (步驟 1-13)", font=("Arial", 12, "bold")).pack(pady=10)
        self.cycle_label = tk.Label(root, text="目前執行次數: 0 / 6", font=("Arial", 10))
        self.cycle_label.pack(pady=5)
        self.status_label = tk.Label(root, text="狀態: 待機中", font=("Arial", 11), fg="blue")
        self.status_label.pack(pady=10)
        self.countdown_label = tk.Label(root, text="下次執行倒數: --:--:--", font=("Consolas", 14, "bold"), fg="green")
        self.countdown_label.pack(pady=10)
        
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=15)
        self.start_btn = tk.Button(btn_frame, text="開始執行", command=self.start, width=15, height=2, bg="#4CAF50", fg="white")
        self.start_btn.pack(side="left", padx=10)
        self.stop_btn = tk.Button(btn_frame, text="停止執行", command=self.stop, width=15, height=2, bg="#f44336", fg="white", state="disabled")
        self.stop_btn.pack(side="left", padx=10)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.stop_requested = False
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            threading.Thread(target=self.main_loop, daemon=True).start()

    def stop(self):
        self.stop_requested = True
        self.status_label.config(text="狀態: 正在請求停止...", fg="red")

    def main_loop(self):
        self.cycle_count = 0
        while self.cycle_count < 6 and not self.stop_requested:
            self.cycle_count += 1
            self.cycle_label.config(text=f"目前執行次數: {self.cycle_count} / 6")
            self.countdown_label.config(text="下次執行倒數: 執行中...")
            
            success = self.run_steps()
            
            if self.stop_requested or not success:
                break
                
            if self.cycle_count < 6:
                wait_seconds = 4 * 3600
                for s in range(wait_seconds, 0, -1):
                    if self.stop_requested: break
                    h = s // 3600
                    m = (s % 3600) // 60
                    sec = s % 60
                    self.countdown_label.config(text=f"下次執行倒數: {h:02d}:{m:02d}:{sec:02d}")
                    self.status_label.config(text="狀態: 等待循環中", fg="green")
                    time.sleep(1)
            else:
                self.countdown_label.config(text="下次執行倒數: 已全部完成")
        
        self.is_running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        if self.stop_requested:
            self.status_label.config(text="狀態: 已停止 (歸零)", fg="red")
            self.cycle_label.config(text="目前執行次數: 0 / 6")
            self.countdown_label.config(text="下次執行倒數: --:--:--")
        else:
            self.status_label.config(text="狀態: 全部循環完成", fg="blue")

    def run_steps(self):
        base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(".")
        
        for i in range(3, 0, -1):
            if self.stop_requested: return False
            self.status_label.config(text=f"請切換視窗... {i}")
            time.sleep(1)
        
        if self.stop_requested: return False
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
                move_mouse_to(base_x, base_y)
                time.sleep(0.8)
            else:
                pos = pyautogui.position()
                base_x, base_y = pos.x, pos.y
        except: pass

        # 8. 壓住 Alt 並點擊右鍵 20 次
        send_key(SCAN_ALT, False); time.sleep(0.3)
        for _ in range(20):
            if self.stop_requested: break
            mouse_right_click(); time.sleep(0.6)
        send_key(SCAN_ALT, True); time.sleep(0.5)

        # 9. 相對偏移點擊 (左 32, 下 60)
        if self.stop_requested: return False
        move_mouse_to(base_x - 32, base_y + 60); time.sleep(0.5)
        mouse_left_click(); time.sleep(1.0)

        # 10. 回到基準點, Alt + 右鍵 10 次
        if self.stop_requested: return False
        move_mouse_to(base_x, base_y); time.sleep(0.5)
        send_key(SCAN_ALT, False); time.sleep(0.3)
        for _ in range(10):
            if self.stop_requested: break
            mouse_right_click(); time.sleep(0.5)
        send_key(SCAN_ALT, True); time.sleep(0.5)

        # 11. 相對偏移點擊 (左 32, 下 30) + ESC
        if self.stop_requested: return False
        move_mouse_to(base_x - 32, base_y + 30); time.sleep(0.5)
        mouse_left_click(); time.sleep(0.5)
        send_key(SCAN_ESC); time.sleep(0.1); send_key(SCAN_ESC, True)
        
        # --- 步驟 11 完成後，延遲 3 秒 ---
        self.status_label.config(text="等待介面穩定 (3秒)...")
        time.sleep(3.0)

        # 12. 搜尋 'ca2.png' (仿照步驟 7 的結構)
        if self.stop_requested: return False
        self.status_label.config(text="正在搜尋 'ca2.png'...")
        try:
            image_path_ca2 = os.path.join(base_path, "ca2.png")
            location_ca2 = pyautogui.locateOnScreen(image_path_ca2, confidence=0.8)
            if location_ca2:
                # 移動到正中心後，向右 150，向下 60
                tx_ca2 = (location_ca2.left + location_ca2.width // 2) + 150
                ty_ca2 = (location_ca2.top + location_ca2.height // 2) + 60
                
                self.status_label.config(text=f"定位 ca2 成功! 執行偏移點擊")
                move_mouse_to(tx_ca2, ty_ca2)
                time.sleep(0.5)
                mouse_left_click()
                
                # 點擊後等待 1 秒
                time.sleep(1.0)
            else:
                self.status_label.config(text="未找到圖片 'ca2.png'")
                time.sleep(1.5)
        except: pass

        # 13. 按 X 鍵
        if self.stop_requested: return False
        send_key(SCAN_X); time.sleep(0.1); send_key(SCAN_X, True); time.sleep(0.5)
        return True

if __name__ == "__main__":
    root = tk.Tk()
    app = CustomApp(root)
    root.mainloop()
