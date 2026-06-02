import tkinter as tk
import time
import threading
import ctypes
import random
import sys
from tkinter import messagebox

# ==========================================
# 最後嘗試方案：管理員權限 + 乾淨的 SendInput 序列
# ==========================================

# 1. 檢查並請求管理員權限 (這對跨視窗輸入至關重要)
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# 定義 Windows API 結構
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
SCANCODE_I = 0x17

user32 = ctypes.WinDLL('user32', use_last_error=True)

def send_input_native(scancode, is_up=False):
    """
    使用最乾淨的參數發送 SendInput。
    有些反作弊會檢查 dwExtraInfo，我們將其設為 0。
    """
    flags = KEYEVENTF_SCANCODE
    if is_up:
        flags |= KEYEVENTF_KEYUP
    
    # 建立輸入物件，dwExtraInfo 設為 0 (None)
    ki = KEYBDINPUT(wVk=0, wScan=scancode, dwFlags=flags, time=0, dwExtraInfo=None)
    ii = INPUT(type=INPUT_KEYBOARD, union=INPUT_UNION(ki=ki))
    
    # 執行發送
    user32.SendInput(1, ctypes.byref(ii), ctypes.sizeof(ii))

def press_i_final_attempt():
    """執行一次模擬按鍵，加入微小的隨機物理特徵"""
    send_input_native(SCANCODE_I, is_up=False)
    time.sleep(random.uniform(0.06, 0.12)) # 模擬真實按壓時長
    send_input_native(SCANCODE_I, is_up=True)

class FinalAutoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RO 自動化 - 最終測試版")
        self.root.geometry("320x280")
        self.root.attributes("-topmost", True)
        
        self.is_running = False
        
        # UI 佈局
        tk.Label(root, text="狀態診斷", font=("bold", 10)).pack(pady=5)
        self.admin_status = "已取得管理員權限" if is_admin() else "⚠️ 未取得管理員權限"
        tk.Label(root, text=self.admin_status, fg="green" if is_admin() else "red").pack()
        
        self.status_label = tk.Label(root, text="狀態: 待機中", font=("Arial", 12))
        self.status_label.pack(pady=20)
        
        self.start_btn = tk.Button(root, text="開始 (3秒倒數)", command=self.start, 
                                 width=20, height=2, bg="#4CAF50", fg="white")
        self.start_btn.pack(pady=5)
        
        tk.Button(root, text="停止", command=self.stop, width=20).pack(pady=5)
        
        # 說明
        tk.Label(root, text="如果此版本在遊戲中仍無效，\n代表該遊戲已徹底封鎖軟體模擬，\n建議考慮硬體方案。", 
                 fg="gray", font=("Arial", 8)).pack(pady=10)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.start_btn.config(state="disabled")
            threading.Thread(target=self.worker, daemon=True).start()

    def stop(self):
        self.is_running = False
        self.status_label.config(text="狀態: 已停止")
        self.start_btn.config(state="normal")

    def worker(self):
        # 1. 倒數
        for i in range(3, 0, -1):
            if not self.is_running: return
            self.status_label.config(text=f"請切換視窗... {i}")
            time.sleep(1)
        
        if not self.is_running: return
        self.status_label.config(text="正在執行按鍵...")
        
        # 2. 執行 3 次
        for _ in range(3):
            if not self.is_running: break
            press_i_final_attempt()
            time.sleep(random.uniform(0.6, 1.2))
            
        self.is_running = False
        self.status_label.config(text="狀態: 執行完畢")
        self.start_btn.config(state="normal")

if __name__ == "__main__":
    # 如果不是管理員，嘗試重新以管理員身份啟動 (僅在 Windows 且非打包環境下有效)
    # 打包後的 EXE 建議手動「右鍵 -> 以管理員身份執行」
    
    root = tk.Tk()
    app = FinalAutoApp(root)
    root.mainloop()
