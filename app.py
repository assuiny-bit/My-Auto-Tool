import tkinter as tk
import time
import threading
import ctypes
import sys
import pyautogui
import os

# =================================================================
# 終極自動化 V5.0 - 13步驟完整校對版
# =================================================================

# --- 1. 資源路徑處理 (確保 EXE 能讀取內部圖片) ---
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# --- 2. C 語言底層驅動 (SendInput) ---
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

# 掃描碼定義
SCAN_X = 0x2D; SCAN_9 = 0x0A; SCAN_DOWN = 0x50; SCAN_ENTER = 0x1C; SCAN_I = 0x17; SCAN_ALT = 0x38; SCAN_ESC = 0x01

user32 = ctypes.windll.user32
def send_input(ii):
    user32.SendInput(1, ctypes.byref(ii), ctypes.sizeof(ii))

def move_mouse_to(x, y):
    nx = int(x * 65536 / user32.GetSystemMetrics(0))
    ny = int(y * 65536 / user32.GetSystemMetrics(1))
    mi = MOUSEINPUT(dx=nx, dy=ny, mouseData=0, dwFlags=0x0001 | 0x8000, time=0, dwExtraInfo=None)
    send_input(INPUT(type=0, union=INPUT_UNION(mi=mi)))

def mouse_left_click():
    send_input(INPUT(type=0, union=INPUT_UNION(mi=MOUSEINPUT(0,0,0,0x0002,0,None)))) # Down
    time.sleep(0.1)
    send_input(INPUT(type=0, union=INPUT_UNION(mi=MOUSEINPUT(0,0,0,0x0004,0,None)))) # Up

def mouse_right_click():
    send_input(INPUT(type=0, union=INPUT_UNION(mi=MOUSEINPUT(0,0,0,0x0008,0,None)))) # Down
    time.sleep(0.1)
    send_input(INPUT(type=0, union=INPUT_UNION(mi=MOUSEINPUT(0,0,0,0x0010,0,None)))) # Up

def send_key(scancode, is_up=False):
    flags = 0x0008 # SCANCODE
    if is_up: flags |= 0x0002 # KEYUP
    ki = KEYBDINPUT(0, scancode, flags, 0, None)
    send_input(INPUT(type=1, union=INPUT_UNION(ki=ki)))

# --- 3. GUI 與主邏輯 ---
class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("終極自動化 V5.0")
        self.root.geometry("350x400")
        self.root.attributes("-topmost", True)
        self.is_running = False
        self.stop_requested = False
        
        tk.Label(root, text="自動化流程 (13步驟完整版)", font=("Arial", 12, "bold")).pack(pady=10)
        self.status_label = tk.Label(root, text="狀態: 待機中", font=("Arial", 10), fg="blue")
        self.status_label.pack(pady=5)
        self.countdown_label = tk.Label(root, text="下次執行倒數: --:--:--", font=("Consolas", 14, "bold"), fg="green")
        self.countdown_label.pack(pady=10)
        
        self.start_btn = tk.Button(root, text="開始執行", command=self.start, width=15, height=2, bg="green", fg="white")
        self.start_btn.pack(pady=5)
        self.stop_btn = tk.Button(root, text="停止執行", command=self.stop, width=15, height=2, bg="red", fg="white", state="disabled")
        self.stop_btn.pack(pady=5)

    def start(self):
        self.is_running = True
        self.stop_requested = False
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        threading.Thread(target=self.main_loop, daemon=True).start()

    def stop(self):
        self.stop_requested = True
        self.status_label.config(text="狀態: 停止中...", fg="red")

    def main_loop(self):
        for cycle in range(6):
            if self.stop_requested: break
            self.run_steps()
            if self.stop_requested or cycle == 5: break
            
            # 4 小時循環
            wait_time = 4 * 3600
            for s in range(wait_time, 0, -1):
                if self.stop_requested: break
                h, m, sec = s // 3600, (s % 3600) // 60, s % 60
                self.countdown_label.config(text=f"{h:02d}:{m:02d}:{sec:02d}")
                time.sleep(1)
        
        self.is_running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def run_steps(self):
        # 啟動倒數
        for i in range(3, 0, -1):
            if self.stop_requested: return
            self.status_label.config(text=f"準備開始... {i}")
            time.sleep(1)

        # 步驟 1-5
        self.status_label.config(text="步驟 1-5: 基礎按鍵")
        send_key(SCAN_X); time.sleep(0.1); send_key(SCAN_X, True); time.sleep(1) # Step 1-2
        send_key(SCAN_9); time.sleep(0.1); send_key(SCAN_9, True); time.sleep(0.5) # Step 3-4
        send_key(SCAN_DOWN); time.sleep(0.1); send_key(SCAN_DOWN, True); time.sleep(0.5) # Step 5
        for _ in range(2): # Step 7 (Enter x2)
            send_key(SCAN_ENTER); time.sleep(0.1); send_key(SCAN_ENTER, True); time.sleep(0.7)
        send_key(SCAN_I); time.sleep(0.1); send_key(SCAN_I, True); time.sleep(0.5) # Step 9

        # 步驟 7: 搜尋 01.png (建立 bx, by 基準)
        self.status_label.config(text="步驟 7: 搜尋 01.png...")
        bx, by = pyautogui.position().x, pyautogui.position().y # 預設值
        try:
            loc = pyautogui.locateOnScreen(resource_path("01.png"), confidence=0.8)
            if loc:
                bx = (loc.left + loc.width // 2) + 32
                by = (loc.top + loc.height // 2) - 30
                move_mouse_to(bx, by); time.sleep(0.8)
        except: pass

        # 步驟 8: Alt + 右鍵 20次
        self.status_label.config(text="步驟 8: Alt + 右鍵 20次")
        send_key(SCAN_ALT); time.sleep(0.3)
        for _ in range(20):
            if self.stop_requested: break
            mouse_right_click(); time.sleep(0.6)
        send_key(SCAN_ALT, True); time.sleep(0.5)

        # 步驟 9: 偏移點擊
        move_mouse_to(bx - 32, by + 60); time.sleep(0.5); mouse_left_click(); time.sleep(1)

        # 步驟 10: Alt + 右鍵 10次
        move_mouse_to(bx, by); time.sleep(0.5); send_key(SCAN_ALT); time.sleep(0.3)
        for _ in range(10):
            if self.stop_requested: break
            mouse_right_click(); time.sleep(0.5)
        send_key(SCAN_ALT, True); time.sleep(0.5)

        # 步驟 11: 偏移點擊 + ESC
        move_mouse_to(bx - 32, by + 30); time.sleep(0.5); mouse_left_click(); time.sleep(0.5)
        send_key(SCAN_ESC); time.sleep(0.1); send_key(SCAN_ESC, True); time.sleep(3)

        # 步驟 12: [重新修改] 搜尋 ca2.png 並點擊正中心
        self.status_label.config(text="步驟 12: 搜尋 ca2.png 並點擊中心")
        try:
            # 使用與步驟 7 相同的搜尋邏輯
            loc_ca2 = pyautogui.locateOnScreen(resource_path("ca2.png"), confidence=0.8)
            if loc_ca2:
                # 計算圖片正中心
                center_x = loc_ca2.left + loc_ca2.width // 2
                center_y = loc_ca2.top + loc_ca2.height // 2
                move_mouse_to(center_x, center_y)
                time.sleep(0.5)
                mouse_left_click()
                self.status_label.config(text="ca2 點擊成功，等待 1 秒")
                time.sleep(1.0) # 點擊後等待 1 秒
            else:
                self.status_label.config(text="未找到 ca2.png，跳過")
                time.sleep(1.0)
        except Exception as e:
            print(f"Error in Step 12: {e}")

        # 步驟 13: 按 X
        self.status_label.config(text="步驟 13: 按 X 結束本輪")
        send_key(SCAN_X); time.sleep(0.1); send_key(SCAN_X, True)
        self.status_label.config(text="本輪執行完畢")

if __name__ == "__main__":
    root = tk.Tk(); app = MainApp(root); root.mainloop()
