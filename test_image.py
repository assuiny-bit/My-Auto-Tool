import tkinter as tk
import time
import threading
import ctypes
import pyautogui
import os

# --- 底層 C 語言驅動 ---
user32 = ctypes.windll.user32
def move_mouse_to(x, y):
    nx = int(x * 65536 / user32.GetSystemMetrics(0))
    ny = int(y * 65536 / user32.GetSystemMetrics(1))
    user32.mouse_event(0x0001 | 0x8000, nx, ny, 0, 0)

def mouse_left_click():
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.1)
    user32.mouse_event(0x0004, 0, 0, 0, 0)

def send_x():
    user32.keybd_event(0, 0x2D, 0x0008, 0)
    time.sleep(0.1)
    user32.keybd_event(0, 0x2D, 0x0008 | 0x0002, 0)

class TestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("驗證器")
        self.root.geometry("300x200")
        self.root.attributes("-topmost", True)
        tk.Label(root, text="驗證流程：\n1. 按 X\n2. 找 CLOSS 並點擊", pady=20).pack()
        self.btn = tk.Button(root, text="開始驗證", command=self.start_test, bg="green", fg="white")
        self.btn.pack()
        self.status = tk.Label(root, text="狀態: 待機")
        self.status.pack(pady=10)

    def start_test(self):
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        for i in range(3, 0, -1):
            self.status.config(text=f"倒數 {i} 秒...")
            time.sleep(1)
        send_x()
        time.sleep(1)
        try:
            # 搜尋同資料夾下的 CLOSS.png
            loc = pyautogui.locateOnScreen("CLOSS.png", confidence=0.7)
            if loc:
                move_mouse_to(loc.left + loc.width // 2, loc.top + loc.height // 2)
                time.sleep(0.5)
                mouse_left_click()
                self.status.config(text="成功！")
            else:
                self.status.config(text="失敗：找不到圖片")
        except Exception as e:
            self.status.config(text=f"錯誤: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TestApp(root)
    root.mainloop()
