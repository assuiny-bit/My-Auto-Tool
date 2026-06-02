import tkinter as tk
import time
import threading
import ctypes
import random
import sys
from tkinter import messagebox

# =================================================================
# C 強化版：透過 Python 呼叫底層 NtUserSendInput API
# 嘗試繞過 User32.dll 的監控，直接呼叫更底層的輸入函數。
# =================================================================

# 1. 定義 Windows C-style 結構體 (與 SendInput 相同)
# 這些結構體必須嚴格遵守 Windows API 的記憶體對齊規範
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

# 2. 定義系統常數
INPUT_KEYBOARD = 1
KEYEVENTF_SCANCODE = 0x0008  # 使用硬體掃描碼模式
KEYEVENTF_KEYUP = 0x0002     # 代表放開按鍵
SCAN_I = 0x17                # 'I' 鍵的硬體掃描碼

# 3. 載入 win32u.dll 並獲取 NtUserSendInput 函數
# 這是一個未公開的 API，需要動態獲取
try:
    # 嘗試直接載入 win32u.dll
    win32u = ctypes.WinDLL('win32u.dll', use_last_error=True)
    # 獲取 NtUserSendInput 函數的位址
    NtUserSendInput = win32u.NtUserSendInput
    # 定義函數原型 (參數類型和返回值)
    NtUserSendInput.argtypes = (
        ctypes.c_ulong,
        ctypes.POINTER(INPUT),
        ctypes.c_int
    )
    NtUserSendInput.restype = ctypes.c_ulong
    print("NtUserSendInput loaded successfully from win32u.dll")
except Exception as e:
    print(f"Failed to load NtUserSendInput from win32u.dll: {e}")
    NtUserSendInput = None # 如果載入失敗，則設為 None

# 4. 輔助函數：發送底層按鍵事件
def send_key_event_nt(scancode, is_up=False):
    """
    透過 NtUserSendInput 發送底層按鍵事件。
    如果 NtUserSendInput 載入失敗，則退回使用 User32.dll 的 SendInput。
    """
    flags = KEYEVENTF_SCANCODE
    if is_up:
        flags |= KEYEVENTF_KEYUP
    
    ki = KEYBDINPUT(wVk=0, wScan=scancode, dwFlags=flags, time=0, dwExtraInfo=None)
    ii = INPUT(type=INPUT_KEYBOARD, union=INPUT_UNION(ki=ki))
    
    if NtUserSendInput:
        # 嘗試呼叫 NtUserSendInput
        result = NtUserSendInput(1, ctypes.byref(ii), ctypes.sizeof(ii))
        if result == 0:
            # 如果 NtUserSendInput 返回 0，表示失敗，可能是權限或被攔截
            print("NtUserSendInput failed, falling back to User32.SendInput")
            ctypes.windll.user32.SendInput(1, ctypes.byref(ii), ctypes.sizeof(ii))
    else:
        # 如果 NtUserSendInput 未載入，直接使用 User32.dll 的 SendInput
        ctypes.windll.user32.SendInput(1, ctypes.byref(ii), ctypes.sizeof(ii))

class CEnhancedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("C 強化版輸入測試")
        self.root.geometry("380x350")
        self.root.attributes("-topmost", True)
        
        self.is_running = False
        
        tk.Label(root, text="Python C 強化版輸入測試", font=("Arial", 12, "bold")).pack(pady=10)
        
        # 權限檢查顯示
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        admin_text = "管理員權限: 已取得" if is_admin else "管理員權限: 未取得 (請右鍵執行)"
        tk.Label(root, text=admin_text, fg="green" if is_admin else "red", font=("Arial", 9)).pack()

        # NtUserSendInput 載入狀態
        nt_status_text = "NtUserSendInput: 已載入" if NtUserSendInput else "NtUserSendInput: 載入失敗 (將使用 User32.SendInput)"
        nt_status_color = "green" if NtUserSendInput else "orange"
        tk.Label(root, text=nt_status_text, fg=nt_status_color, font=("Arial", 9)).pack()

        self.status_label = tk.Label(root, text="狀態: 待機中", font=("Arial", 11))
        self.status_label.pack(pady=20)

        self.start_btn = tk.Button(root, text="開始執行 (3秒倒數)", command=self.start, 
                                 width=20, height=2, bg="#FF5722", fg="white")
        self.start_btn.pack(pady=5)

        tk.Button(root, text="停止執行", command=self.stop, width=20).pack(pady=5)
        
        tk.Label(root, text="測試目標：在倒數結束前切換到記事本或遊戲，\n觀察程式如何發送 3 次 'I' 鍵訊號。\n\n注意：此為實驗性功能，可能觸發反作弊。", 
                 fg="#666", font=("Arial", 9)).pack(pady=15)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.start_btn.config(state="disabled")
            threading.Thread(target=self.run_sequence, daemon=True).start()

    def stop(self):
        self.is_running = False
        self.status_label.config(text="狀態: 已手動停止")
        self.start_btn.config(state="normal")

    def run_sequence(self):
        # 1. 倒數階段
        for i in range(3, 0, -1):
            if not self.is_running: return
            self.status_label.config(text=f"準備切換視窗... {i}")
            time.sleep(1)
        
        if not self.is_running: return
        self.status_label.config(text="正在執行 C 強化版 API 模擬...")
        
        # 2. 執行按鍵循環 (執行 3 次)
        for count in range(1, 4):
            if not self.is_running: break
            
            self.status_label.config(text=f"執行第 {count} 次按鍵模擬...")
            
            # 按下
            send_key_event_nt(SCAN_I, is_up=False)
            # 模擬物理按壓時長 (0.05 ~ 0.15 秒)
            time.sleep(random.uniform(0.05, 0.15))
            # 放開
            send_key_event_nt(SCAN_I, is_up=True)
            
            # 兩次按鍵之間的間隔 (1.0 秒)
            if count < 3:
                time.sleep(1.0)
            
        self.is_running = False
        self.status_label.config(text="狀態: 練習流程結束")
        self.start_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = CEnhancedApp(root)
    root.mainloop()
