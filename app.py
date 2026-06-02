import tkinter as tk
import time
import threading
import ctypes
import random

# =================================================================
# 降級優化版：使用舊式 keybd_event API
# 有時候越簡單的方法，越能避開複雜的反作弊檢查。
# =================================================================

# 定義虛擬鍵碼 (Virtual Key Codes)
VK_I = 0x49  # 'I' 鍵的虛擬鍵碼
KEYEVENTF_KEYUP = 0x0002

user32 = ctypes.windll.user32

def simple_press_i():
    """使用最傳統的 keybd_event 模擬按鍵"""
    # 按下
    user32.keybd_event(VK_I, 0, 0, 0)
    # 隨機按住一小段時間
    time.sleep(random.uniform(0.05, 0.1))
    # 放開
    user32.keybd_event(VK_I, 0, KEYEVENTF_KEYUP, 0)

class SimpleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("相容性測試工具")
        self.root.geometry("300x250")
        self.root.attributes("-topmost", True)
        
        self.is_running = False
        
        tk.Label(root, text="傳統模式測試", font=("Arial", 12, "bold")).pack(pady=10)
        
        self.status_label = tk.Label(root, text="狀態: 待機中", font=("Arial", 11))
        self.status_label.pack(pady=20)

        self.start_btn = tk.Button(root, text="開始 (3秒倒數)", command=self.start, 
                                 width=20, height=2, bg="#FF9800", fg="white")
        self.start_btn.pack(pady=5)

        tk.Button(root, text="停止", command=self.stop, width=20).pack(pady=5)

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
        # 1. 倒數
        for i in range(3, 0, -1):
            if not self.is_running: return
            self.status_label.config(text=f"請切換視窗... {i}")
            time.sleep(1)
        
        if not self.is_running: return
        
        # 2. 執行 3 次，間隔 1 秒
        for count in range(1, 4):
            if not self.is_running: break
            self.status_label.config(text=f"執行第 {count} 次...")
            
            simple_press_i()
            
            if count < 3:
                time.sleep(1.0)
            
        self.is_running = False
        self.status_label.config(text="狀態: 完成")
        self.start_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleApp(root)
    root.mainloop()
