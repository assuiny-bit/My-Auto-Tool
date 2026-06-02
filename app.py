import tkinter as tk
import time
import threading
import ctypes
import random
import sys

# 定義 SendInput 結構體和常數
# https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-input
# https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-keybdinput

# C-style structure for KEYBDINPUT
class KEYBDINPUT(ctypes.Structure ):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]

# C-style structure for HARDWAREINPUT
class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_ushort),
        ("wParamH", ctypes.c_ushort),
    ]

# C-style structure for MOUSEINPUT
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]

# C-style union for INPUT
class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]

# C-style structure for INPUT
class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("union", INPUT_UNION),
    ]

# Input types
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

# Key event flags
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_UNICODE = 0x0004

# Virtual key codes (for reference, not used with scan codes directly)
VK_I = 0x49 # 'I' key

# Scan code for 'I' key (standard US keyboard layout)
# You can find scan codes using tools like 'Keyboard Scan Code Viewer'
SCANCODE_I = 0x17

# User32 library for SendInput
user32 = ctypes.WinDLL('user32', use_last_error=True)

def send_input(inputs):
    """Wrapper for SendInput function."""
    nInputs = len(inputs)
    LPINPUT = INPUT * nInputs
    pInputs = LPINPUT(*inputs)
    cbSize = ctypes.c_int(ctypes.sizeof(INPUT))
    return user32.SendInput(nInputs, pInputs, cbSize)

def press_key_scancode(scancode, delay_min=0.05, delay_max=0.15):
    """模擬按下並釋放一個鍵盤按鍵，使用掃描碼和隨機延遲。"""
    # Press key
    x = INPUT(type=INPUT_KEYBOARD, union=INPUT_UNION(ki=KEYBDINPUT(wVk=0, wScan=scancode, dwFlags=KEYEVENTF_SCANCODE, time=0, dwExtraInfo=None)))
    send_input([x])
    time.sleep(random.uniform(delay_min, delay_max))

    # Release key
    x = INPUT(type=INPUT_KEYBOARD, union=INPUT_UNION(ki=KEYBDINPUT(wVk=0, wScan=scancode, dwFlags=KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, time=0, dwExtraInfo=None)))
    send_input([x])
    time.sleep(random.uniform(delay_min, delay_max))

class AutoKeyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RO 自動按鍵輔助")
        self.root.geometry("300x250")
        self.root.attributes("-topmost", True) # 視窗置頂
        
        self.is_running = False
        self.task_thread = None
        
        # 狀態顯示
        self.status_label = tk.Label(root, text="狀態: 待機中", font=("Microsoft JhengHei", 12))
        self.status_label.pack(pady=20)
        
        # 開始按鈕
        self.start_btn = tk.Button(root, text="開始執行", command=self.start_task, 
                                 width=15, height=2, bg="#4CAF50", fg="white", font=("bold"))
        self.start_btn.pack(pady=5)
        
        # 停止按鈕
        self.stop_btn = tk.Button(root, text="停止並重設", command=self.stop_task, 
                                width=15, height=2, bg="#f44336", fg="white", font=("bold"))
        self.stop_btn.pack(pady=5)

        # 診斷訊息
        self.diag_label = tk.Label(root, text="", wraplength=280, justify="left", fg="gray")
        self.diag_label.pack(pady=10)
        self.diag_label.config(text="注意：此工具使用 SendInput 掃描碼模擬，可能仍被遊戲反作弊偵測。")

    def start_task(self):
        if not self.is_running:
            self.is_running = True
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.task_thread = threading.Thread(target=self.run_sequence, daemon=True)
            self.task_thread.start()

    def stop_task(self):
        self.is_running = False
        if self.task_thread and self.task_thread.is_alive():
            # Give thread a moment to stop gracefully
            self.status_label.config(text="狀態: 正在停止...")
        else:
            self.status_label.config(text="狀態: 已停止")
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")

    def run_sequence(self):
        try:
            # 1. 倒數 3 秒讓使用者切換視窗
            for i in range(3, 0, -1):
                if not self.is_running:
                    return
                self.status_label.config(text=f"請切換到遊戲... {i}")
                time.sleep(1)
            
            if not self.is_running:
                return
            self.status_label.config(text="正在執行按鍵 (I x3)...")
            
            # 2. 執行按 3 下 I 鍵
            for _ in range(3):
                if not self.is_running:
                    break
                press_key_scancode(SCANCODE_I, delay_min=0.08, delay_max=0.18) # 每次按鍵間隔隨機化
                time.sleep(random.uniform(0.5, 1.0)) # 每次按鍵間的延遲
                
            # 3. 結束流程
            self.is_running = False
            self.status_label.config(text="狀態: 執行完畢")

        except Exception as e:
            self.status_label.config(text=f"錯誤: {e}")
        finally:
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")

if __name__ == "__main__":
    if sys.platform != "win32":
        messagebox.showerror("錯誤", "此工具僅支援 Windows 作業系統。")
        sys.exit(1)
    root = tk.Tk()
    app = AutoKeyApp(root)
    root.mainloop()
