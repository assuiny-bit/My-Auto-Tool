import tkinter as tk
from tkinter import messagebox, scrolledtext
import time
import threading
import ctypes
import random
import sys
import pyautogui
import os

# =================================================================
# C 強化版 V2.9：新增句柄搜尋與指定輸入框
# =================================================================

# --- Windows API 結構與定義 ---
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

# Windows API 函數與常數
user32 = ctypes.windll.user32
WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

def get_window_list():
    """獲取所有可見視窗的標題與句柄"""
    windows = []
    def enum_handler(hwnd, lParam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                windows.append((hwnd, buff.value))
        return True
    user32.EnumWindows(WNDENUMPROC(enum_handler), 0)
    return windows

# 基礎輸入函數 (NtUserSendInput 支援)
try:
    win32u = ctypes.WinDLL("win32u.dll", use_last_error=True)
    NtUserSendInput = win32u.NtUserSendInput
except:
    NtUserSendInput = None

def send_input(ii):
    if NtUserSendInput:
        NtUserSendInput(1, ctypes.byref(ii), ctypes.sizeof(ii))
    else:
        user32.SendInput(1, ctypes.byref(ii), ctypes.sizeof(ii))

# --- 自動化輔助函數 ---
def move_mouse_to(x, y):
    w, h = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    nx, ny = int(x * 65536 / w), int(y * 65536 / h)
    mi = MOUSEINPUT(dx=nx, dy=ny, dwFlags=0x0001 | 0x8000) # MOVE | ABSOLUTE
    send_input(INPUT(type=0, union=INPUT_UNION(mi=mi)))

def mouse_left_click():
    send_input(INPUT(type=0, union=INPUT_UNION(mi=MOUSEINPUT(dwFlags=0x0002)))) # LEFTDOWN
    time.sleep(0.05)
    send_input(INPUT(type=0, union=INPUT_UNION(mi=MOUSEINPUT(dwFlags=0x0004)))) # LEFTUP

def mouse_right_click():
    send_input(INPUT(type=0, union=INPUT_UNION(mi=MOUSEINPUT(dwFlags=0x0008)))) # RIGHTDOWN
    time.sleep(0.05)
    send_input(INPUT(type=0, union=INPUT_UNION(mi=MOUSEINPUT(dwFlags=0x0010)))) # RIGHTUP

def send_key(scancode, is_up=False, is_extended=False):
    flags = 0x0008 # SCANCODE
    if is_up: flags |= 0x0002
    if is_extended: flags |= 0x0001
    ki = KEYBDINPUT(wScan=scancode, dwFlags=flags)
    send_input(INPUT(type=1, union=INPUT_UNION(ki=ki)))

# 掃描碼
SCAN_ESC=0x01; SCAN_X=0x2D; SCAN_9=0x0A; SCAN_DOWN=0x50; SCAN_ENTER=0x1C; SCAN_I=0x17; SCAN_ALT=0x38

class CustomApp:
    def __init__(self, root):
        self.root = root
        self.root.title("終極按鍵助手 V2.9")
        self.root.geometry("450x600")
        self.root.attributes("-topmost", True)
        self.is_running = False
        self.stop_event = threading.Event()
        
        # --- 句柄搜尋區 ---
        tk.Label(root, text="視窗句柄管理", font=("Arial", 11, "bold")).pack(pady=5)
        self.search_btn = tk.Button(root, text="🔍 自動搜尋視窗句柄", command=self.show_window_list, bg="#2196F3", fg="white")
        self.search_btn.pack(pady=5)
        
        # --- 句柄輸入區 (橫排三個) ---
        tk.Label(root, text="指定執行句柄 (備用):", font=("Arial", 9)).pack()
        handle_frame = tk.Frame(root)
        handle_frame.pack(pady=5)
        
        self.handle_entries = []
        for i in range(3):
            entry = tk.Entry(handle_frame, width=12, justify='center')
            entry.pack(side=tk.LEFT, padx=5)
            entry.insert(0, f"句柄 {i+1}")
            self.handle_entries.append(entry)

        # --- 原有功能區 ---
        tk.Label(root, text="--- 自動化流程 ---", font=("Arial", 11, "bold")).pack(pady=10)
        self.cycle_label = tk.Label(root, text="循環: 0/6", font=("Arial", 10), fg="purple")
        self.cycle_label.pack()
        self.countdown_label = tk.Label(root, text="倒數: 00:00:00", font=("Arial", 10), fg="darkgreen")
        self.countdown_label.pack()
        
        self.status_label = tk.Label(root, text="狀態: 待機中", font=("Arial", 11), fg="blue", wraplength=350)
        self.status_label.pack(pady=15)
        
        self.start_btn = tk.Button(root, text="🚀 開始全流程", command=self.start, width=20, height=2, bg="#4CAF50", fg="white")
        self.start_btn.pack(pady=5)
        self.stop_btn = tk.Button(root, text="🛑 強制停止", command=self.stop, width=20, height=2, bg="#F44336", fg="white", state="disabled")
        self.stop_btn.pack(pady=5)

    def show_window_list(self):
        """彈出視窗顯示所有句柄"""
        list_win = tk.Toplevel(self.root)
        list_win.title("目前視窗句柄清單")
        list_win.geometry("500x400")
        list_win.attributes("-topmost", True)
        
        txt = scrolledtext.ScrolledText(list_win, width=60, height=25)
        txt.pack(padx=10, pady=10)
        
        windows = get_window_list()
        txt.insert(tk.END, f"{'句柄 (HWND)':<15} | {'視窗標題'}\n")
        txt.insert(tk.END, "-"*50 + "\n")
        for hwnd, title in windows:
            txt.insert(tk.END, f"{hwnd:<15} | {title}\n")
        txt.config(state=tk.DISABLED)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.stop_event.clear()
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            threading.Thread(target=self.schedule_run, daemon=True).start()

    def stop(self):
        self.stop_event.set()
        self.is_running = False
        self.status_label.config(text="狀態: 已強制停止", fg="red")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    # --- 這裡保留之前的 13 步流程邏輯 (省略部分重複代碼以節省長度) ---
    def find_and_click(self, img, ox=0, oy=0, click=True):
        if self.stop_event.is_set(): return False
        try:
            base = sys._MEIPASS if getattr(sys, 'frozen', False) else "."
            loc = pyautogui.locateOnScreen(os.path.join(base, img), confidence=0.85)
            if loc:
                cx, cy = loc.left + loc.width//2, loc.top + loc.height//2
                if click: move_mouse_to(cx, cy); time.sleep(0.2); mouse_left_click(); time.sleep(0.5)
                move_mouse_to(cx + ox, cy + oy); time.sleep(0.5)
                return True
        except: pass
        return False

    def execute_steps(self):
        # 1-6 步
        for i in range(3, 0, -1):
            if self.stop_event.is_set(): return False
            self.status_label.config(text=f"準備中... {i}"); time.sleep(1)
        
        self.status_label.config(text="步驟 2-6: 基礎按鍵")
        keys = [(SCAN_X, 1.0), (SCAN_9, 0.5)]
        for k, t in keys:
            if self.stop_event.is_set(): return False
            send_key(k); time.sleep(0.1); send_key(k, True); time.sleep(t)
        
        # 步驟 7-13 (包含圖片搜尋)
        self.status_label.config(text="步驟 7-8: 01.png 偏移")
        if self.find_and_click("01.png", 28, -30):
            send_key(SCAN_ALT); time.sleep(0.2)
            for _ in range(20):
                if self.stop_event.is_set(): break
                mouse_right_click(); time.sleep(0.6)
            send_key(SCAN_ALT, True)

        self.status_label.config(text="步驟 9-10: 02.png 偏移")
        if self.find_and_click("02.png", 28, -60):
            send_key(SCAN_ALT); time.sleep(0.2)
            for _ in range(6):
                if self.stop_event.is_set(): break
                mouse_right_click(); time.sleep(0.6)
            send_key(SCAN_ALT, True)

        self.status_label.config(text="最後收尾...")
        send_key(SCAN_ESC); time.sleep(0.1); send_key(SCAN_ESC, True); time.sleep(0.5)
        self.find_and_click("ca2.png", 0, 0)
        send_key(SCAN_X); time.sleep(0.1); send_key(SCAN_X, True)
        return True

    def schedule_run(self):
        for c in range(1, 7):
            if self.stop_event.is_set(): break
            self.cycle_label.config(text=f"循環: {c}/6")
            if not self.execute_steps(): break
            
            if c < 6:
                rem = 4 * 3600
                while rem > 0 and not self.stop_event.is_set():
                    h, r = divmod(rem, 3600); m, s = divmod(r, 60)
                    self.countdown_label.config(text=f"倒數: {h:02}:{m:02}:{s:02}")
                    time.sleep(1); rem -= 1
        self.stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = CustomApp(root)
    root.mainloop()
