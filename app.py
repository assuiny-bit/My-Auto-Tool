import tkinter as tk
import time
import threading
import ctypes
import random
import sys

# =================================================================
# Windows 輸入 API 技術練習工具 (慢速穩定版)
# 調整內容：
# 1. 每次按鍵間隔固定為 1 秒。
# 2. 模擬更緩慢、穩定的按鍵動作。
# =================================================================

# 定義 Windows API 結構體
class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_ushort),
        ("wParamH", ctypes.c_ushort),
    ]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]

class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]

class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("union", INPUT_UNION)]

INPUT_KEYBOARD = 1
KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_KEYUP = 0x0002
SCAN_I = 0x17

user32 = ctypes.WinDLL('user32', use_last_error=True)

def send_key_event(scancode, is_up=False):
    flags = KEYEVENTF_SCANCODE
    if is_up:
        flags |= KEYEVENTF_KEYUP
    ki = KEYBDINPUT(wVk=0, wScan=scancode, dwFlags=flags, time=0, dwExtraInfo=None)
    ii = INPUT(type=INPUT_KEYBOARD, union=INPUT_UNION(ki=ki))
    user32.SendInput(1, ctypes.byref(ii), ctypes.sizeof(ii))

class SlowKeyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("慢速按鍵測試工具")
        self.root.geometry("350x300")
        self.root.attributes("-topmost", True)
        
        self.is_running = False
        
        tk.Label(root, text="慢速按鍵練習 (間隔 1 秒)", font=("Arial", 12, "bold")).pack(pady=10)
        
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        admin_text = "管理員權限: 已取得" if is_admin else "管理員權限: 未取得 (請右鍵執行)"
        tk.Label(root, text=admin_text, fg="green" if is_admin else "red").pack()

        self.status_label = tk.Label(root, text="狀態: 待機中", font=("Arial", 11))
        self.status_label.pack(pady=20)

        self.start_btn = tk.Button(root, text="開始執行 (3秒倒數)", command=self.start, 
                                 width=20, height=2, bg="#4CAF50", fg="white")
        self.start_btn.pack(pady=5)

        tk.Button(root, text="停止", command=self.stop, width=20).pack(pady=5)
        
        tk.Label(root, text="執行邏輯：\n1. 倒數 3 秒後開始\n2. 每隔 1 秒按一次 'I'\n3. 總共執行 3 次", 
                 fg="#666", font=("Arial", 9)).pack(pady=15)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.start_btn.config(state="disabled")
            threading.Thread(target=self.run_sequence, daemon=True).start()

    def stop(self):
        self.is_running = False
        self.status_label.config(text="狀態: 已停止")
        self.start_btn.config(state="normal")

    def run_sequence(self):
        # 1. 倒數 3 秒
        for i in range(3, 0, -1):
            if not self.is_running: return
            self.status_label.config(text=f"請切換視窗... {i}")
            time.sleep(1)
        
        if not self.is_running: return
        
        # 2. 執行 3 次循環
        for count in range(1, 4):
            if not self.is_running: break
            
            self.status_label.config(text=f"正在發送第 {count} 次按鍵...")
            
            # 按下 (模擬較緩慢的按壓，持續 0.15 秒)
            send_key_event(SCAN_I, is_up=False)
            time.sleep(0.15) 
            
            # 放開
            send_key_event(SCAN_I, is_up=True)
            
            # 如果不是最後一次，就等待 1 秒再進行下一次
            if count < 3:
                self.status_label.config(text=f"等待 1 秒後進行下次按鍵...")
                time.sleep(1.0)
            
        self.is_running = False
        self.status_label.config(text="狀態: 流程已完成")
        self.start_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = SlowKeyApp(root)
    root.mainloop()
