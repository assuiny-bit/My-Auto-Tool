import tkinter as tk
import time
import threading
import ctypes
import sys
import pyautogui
import os

# =================================================================
# 終極自動化 V7.0 - 絕對不簡化、完整 C 語言驅動定稿版
# =================================================================

# --- 1. 資源路徑處理 (確保 EXE 能讀取內部圖片) ---
def resource_path(relative_path):
    """ 獲取打包後資源的絕對路徑，確保圖片能被讀取 """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# --- 2. 完整的 C 語言底層結構體定義 (絕對不簡化) ---
# 這些定義是為了讓 Windows SendInput 函式能精準識別指令

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_ushort),
        ("wParamH", ctypes.c_ushort)
    ]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]

class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("union", INPUT_UNION)]

# 鍵盤掃描碼定義
SCAN_X = 0x2D
SCAN_9 = 0x0A
SCAN_DOWN = 0x50
SCAN_ENTER = 0x1C
SCAN_I = 0x17
SCAN_ALT = 0x38
SCAN_ESC = 0x01

# 載入 Windows User32 函式庫
user32 = ctypes.windll.user32

def send_input(ii):
    """ 核心發送函式 """
    user32.SendInput(1, ctypes.byref(ii), ctypes.sizeof(ii))

def move_mouse_to(x, y):
    """ 移動滑鼠到絕對座標 """
    nx = int(x * 65536 / user32.GetSystemMetrics(0))
    ny = int(y * 65536 / user32.GetSystemMetrics(1))
    mi = MOUSEINPUT(dx=nx, dy=ny, mouseData=0, dwFlags=0x0001 | 0x8000, time=0, dwExtraInfo=None)
    send_input(INPUT(type=0, union=INPUT_UNION(mi=mi)))

def mouse_left_click():
    """ 模擬滑鼠左鍵點擊 (按下與放開) """
    # 按下
    mi_down = MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=0x0002, time=0, dwExtraInfo=None)
    send_input(INPUT(type=0, union=INPUT_UNION(mi=mi_down)))
    time.sleep(0.1)
    # 放開
    mi_up = MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=0x0004, time=0, dwExtraInfo=None)
    send_input(INPUT(type=0, union=INPUT_UNION(mi=mi_up)))

def mouse_right_click():
    """ 模擬滑鼠右鍵點擊 (按下與放開) """
    # 按下
    mi_down = MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=0x0008, time=0, dwExtraInfo=None)
    send_input(INPUT(type=0, union=INPUT_UNION(mi=mi_down)))
    time.sleep(0.1)
    # 放開
    mi_up = MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=0x0010, time=0, dwExtraInfo=None)
    send_input(INPUT(type=0, union=INPUT_UNION(mi=mi_up)))

def send_key(scancode, is_up=False):
    """ 模擬鍵盤按鍵 (使用掃描碼) """
    flags = 0x0008 # KEYEVENTF_SCANCODE
    if is_up:
        flags |= 0x0002 # KEYEVENTF_KEYUP
    ki = KEYBDINPUT(wVk=0, wScan=scancode, dwFlags=flags, time=0, dwExtraInfo=None)
    send_input(INPUT(type=1, union=INPUT_UNION(ki=ki)))

# --- 3. GUI 與流程邏輯 ---
class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("終極自動化 V7.0")
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
            
            # 4 小時循環等待
            wait_time = 4 * 3600
            for s in range(wait_time, 0, -1):
                if self.stop_requested: break
                h, m, sec = s // 3600, (s % 3600) // 60, s % 60
                self.countdown_label.config(text=f"下次倒數: {h:02d}:{m:02d}:{sec:02d}")
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

        # 步驟 1-6: 基礎按鍵
        self.status_label.config(text="執行步驟 1-6")
        send_key(SCAN_X); time.sleep(0.1); send_key(SCAN_X, True); time.sleep(1)
        send_key(SCAN_9); time.sleep(0.1); send_key(SCAN_9, True); time.sleep(0.5)
        send_key(SCAN_DOWN); time.sleep(0.1); send_key(SCAN_DOWN, True); time.sleep(0.5)
        for _ in range(2):
            send_key(SCAN_ENTER); time.sleep(0.1); send_key(SCAN_ENTER, True); time.sleep(0.7)
        send_key(SCAN_I); time.sleep(0.1); send_key(SCAN_I, True); time.sleep(0.5)

        # 步驟 7: 搜尋 01.png 並移動 (建立基準點 bx, by)
        self.status_label.config(text="步驟 7: 搜尋 01.png")
        bx, by = pyautogui.position().x, pyautogui.position().y
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
        self.status_label.config(text="步驟 9: 偏移點擊")
        move_mouse_to(bx - 32, by + 60); time.sleep(0.5); mouse_left_click(); time.sleep(1)

        # 步驟 10: Alt + 右鍵 10次
        self.status_label.config(text="步驟 10: Alt + 右鍵 10次")
        move_mouse_to(bx, by); time.sleep(0.5); send_key(SCAN_ALT); time.sleep(0.3)
        for _ in range(10):
            if self.stop_requested: break
            mouse_right_click(); time.sleep(0.5)
        send_key(SCAN_ALT, True); time.sleep(0.5)

        # 步驟 11: 偏移點擊 + ESC
        self.status_label.config(text="步驟 11: 偏移點擊 + ESC")
        move_mouse_to(bx - 32, by + 30); time.sleep(0.5); mouse_left_click(); time.sleep(0.5)
        send_key(SCAN_ESC); time.sleep(0.1); send_key(SCAN_ESC, True); time.sleep(3)

        # 步驟 12: [依照要求完全重寫] 搜尋 ca2.png 並點擊中心
        self.status_label.config(text="步驟 12: 搜尋 ca2.png 中心點擊")
        try:
            # 1. 搜尋圖片
            loc_ca2 = pyautogui.locateOnScreen(resource_path("ca2.png"), confidence=0.8)
            if loc_ca2:
                # 2. 計算正中心位置
                center_x = loc_ca2.left + loc_ca2.width // 2
                center_y = loc_ca2.top + loc_ca2.height // 2
                # 3. 移動游標
                move_mouse_to(center_x, center_y)
                time.sleep(0.5)
                # 4. 按下 1 次滑鼠左鍵
                mouse_left_click()
                self.status_label.config(text="ca2 點擊成功，等待 1 秒")
                # 5. 等待 1 秒
                time.sleep(1.0)
            else:
                self.status_label.config(text="未找到 ca2.png")
                time.sleep(1.0)
        except Exception as e:
            print(f"Step 12 Error: {e}")

        # 步驟 13: 按 X
        self.status_label.config(text="步驟 13: 按 X 結束")
        send_key(SCAN_X); time.sleep(0.1); send_key(SCAN_X, True)
        self.status_label.config(text="本輪執行完畢", fg="green")

if __name__ == "__main__":
    root = tk.Tk(); app = MainApp(root); root.mainloop()
