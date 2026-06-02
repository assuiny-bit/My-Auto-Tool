import tkinter as tk
import time
import threading
import ctypes
import random
import sys
import pyautogui
import os

# =================================================================
# C 強化版 V2.3：底層絕對座標移動 (繞過 SetCursorPos 限制)
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
MOUSEEVENTF_ABSOLUTE = 0x8000 # --- 關鍵：絕對座標模式 ---
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_LEFTDOWN = 0x0002 # --- 新增：左鍵按下 ---
MOUSEEVENTF_LEFTUP = 0x0004   # --- 新增：左鍵放開 ---

SCAN_X = 0x2D; SCAN_9 = 0x0A; SCAN_DOWN = 0x50; SCAN_ENTER = 0x1C; SCAN_I = 0x17; SCAN_ALT = 0x38; SCAN_ESC = 0x01 # --- 新增：ESC 鍵掃描碼 ---

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
    # Windows 底層座標系統將螢幕長寬定義為 0 到 65535
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    # 換算座標
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

def mouse_left_click(): # --- 新增：左鍵點擊功能 ---
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
        self.root.title("底層移動助手 V2.3")
        self.root.geometry("400x380")
        self.root.attributes("-topmost", True)
        self.is_running = False
        
        tk.Label(root, text="底層座標移動模式 (繞過系統攔截)", font=("Arial", 11, "bold")).pack(pady=10)
        self.status_label = tk.Label(root, text="狀態: 待機中", font=("Arial", 11))
        self.status_label.pack(pady=20)
        self.start_btn = tk.Button(root, text="開始執行", command=self.start, width=20, height=2, bg="#FF5722", fg="white")
        self.start_btn.pack(pady=5)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.start_btn.config(state="disabled")
            threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        for i in range(3, 0, -1):
            self.status_label.config(text=f"請切換視窗... {i}")
            time.sleep(1)
        
        # 1-6 步: 鍵盤流程
        self.status_label.config(text="執行: 基礎按鍵序列...")
        send_key(SCAN_X); time.sleep(0.1); send_key(SCAN_X, True); time.sleep(1.0)
        send_key(SCAN_9); time.sleep(0.1); send_key(SCAN_9, True); time.sleep(0.5)
        send_key(SCAN_DOWN, False, True); time.sleep(0.1); send_key(SCAN_DOWN, True, True); time.sleep(0.5)
        for _ in range(2):
            send_key(SCAN_ENTER); time.sleep(0.1); send_key(SCAN_ENTER, True); time.sleep(0.7)
        send_key(SCAN_I); time.sleep(0.1); send_key(SCAN_I, True); time.sleep(0.5)

        # 7. 搜尋圖片並移動 (改用底層移動)
        self.status_label.config(text="正在搜尋 '01.png'...")
        try:
            base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(".")
            image_path = os.path.join(base_path, "01.png")
            location = pyautogui.locateOnScreen(image_path, confidence=0.8)
            if location:
                target_x = (location.left + location.width // 2) + 25
                target_y = (location.top + location.height // 2) - 25
                
                self.status_label.config(text=f"定位成功! 底層移動至 ({target_x}, {target_y})")
                move_mouse_to(target_x, target_y) # --- 使用底層移動 ---
                time.sleep(0.8)
            else:
                self.status_label.config(text="未找到圖片 '01.png'，跳過移動")
                time.sleep(1)
        except Exception as e:
            self.status_label.config(text=f"搜尋 '01.png' 發生錯誤: {e}")
            time.sleep(1)

        # 8. 搜尋圖片 '02.png' 並移動滑鼠至中心向下偏移 10 像素後左鍵點擊
        self.status_label.config(text="正在搜尋 '02.png'...")
        try:
            image_path_02 = os.path.join(base_path, "02.png")
            location_02 = pyautogui.locateOnScreen(image_path_02, confidence=0.8)
            if location_02:
                target_x_02 = location_02.left + location_02.width // 2
                target_y_02 = (location_02.top + location_02.height // 2) + 10 # 向下偏移 10 像素 (0.1 假定為 10 像素)
                
                self.status_label.config(text=f"定位成功! 底層移動至 ({target_x_02}, {target_y_02}) 並左鍵點擊")
                move_mouse_to(target_x_02, target_y_02)
                time.sleep(0.5)
                mouse_left_click()
                time.sleep(0.8)
            else:
                self.status_label.config(text="未找到圖片 '02.png'，跳過步驟 8")
                time.sleep(1)
        except Exception as e:
            self.status_label.config(text=f"搜尋 '02.png' 發生錯誤: {e}")
            time.sleep(1)

        # 9. 從當前位置向右偏移 28 向上偏移 56，壓住 ALT 並右鍵點擊 10 次
        self.status_label.config(text="執行: 壓住 Alt + 底層右鍵 10 次 (偏移後)")
        # 這裡需要知道上一步滑鼠的最終位置，但由於 move_mouse_to 是絕對座標，所以直接計算新的絕對座標
        # 假設上一步的 target_x_02, target_y_02 是當前位置
        if 'location_02' in locals() and location_02:
            current_x = location_02.left + location_02.width // 2
            current_y = (location_02.top + location_02.height // 2) + 10
            target_x_09 = current_x + 28
            target_y_09 = current_y - 56
            move_mouse_to(target_x_09, target_y_09)
            time.sleep(0.5)
        else:
            self.status_label.config(text="無法獲取 '02.png' 位置，步驟 9 將從當前滑鼠位置開始偏移")
            # 如果沒有找到 02.png，則無法進行相對偏移，這裡需要更明確的處理方式
            # 為了測試，暫時假設滑鼠停留在螢幕中央，並進行絕對偏移
            # 實際應用中，如果找不到圖片，可能需要終止或跳過此步驟
            pass # 這裡需要根據實際需求調整

        send_key(SCAN_ALT, False) # 壓住 Alt
        time.sleep(0.3)
        
        for k in range(10):
            if not self.is_running: break
            self.status_label.config(text=f"右鍵點擊: {k+1}/10")
            mouse_right_click()
            time.sleep(0.6)
            
        send_key(SCAN_ALT, True) # 放開 Alt
        time.sleep(0.5)

        # 10. 搜尋圖片 '03.png' 並移動滑鼠至中心向右偏移 20 像素後左鍵點擊
        self.status_label.config(text="正在搜尋 '03.png'...")
        try:
            image_path_03 = os.path.join(base_path, "03.png")
            location_03 = pyautogui.locateOnScreen(image_path_03, confidence=0.8)
            if location_03:
                target_x_03 = (location_03.left + location_03.width // 2) + 20 # 向右偏移 20 像素 (0.2 假定為 20 像素)
                target_y_03 = location_03.top + location_03.height // 2
                
                self.status_label.config(text=f"定位成功! 底層移動至 ({target_x_03}, {target_y_03}) 並左鍵點擊")
                move_mouse_to(target_x_03, target_y_03)
                time.sleep(0.5)
                mouse_left_click()
                time.sleep(0.8)
            else:
                self.status_label.config(text="未找到圖片 '03.png'，跳過步驟 10")
                time.sleep(1)
        except Exception as e:
            self.status_label.config(text=f"搜尋 '03.png' 發生錯誤: {e}")
            time.sleep(1)

        # 11. 搜尋圖片 '01.png' 並移動滑鼠至中心向下偏移 10 像素後左鍵點擊，然後按 ESC
        self.status_label.config(text="正在搜尋 '01.png' (再次)...")
        try:
            image_path_01_again = os.path.join(base_path, "01.png")
            location_01_again = pyautogui.locateOnScreen(image_path_01_again, confidence=0.8)
            if location_01_again:
                target_x_01_again = location_01_again.left + location_01_again.width // 2
                target_y_01_again = (location_01_again.top + location_01_again.height // 2) + 10 # 向下偏移 10 像素 (0.1 假定為 10 像素)
                
                self.status_label.config(text=f"定位成功! 底層移動至 ({target_x_01_again}, {target_y_01_again}) 並左鍵點擊")
                move_mouse_to(target_x_01_again, target_y_01_again)
                time.sleep(0.5)
                mouse_left_click()
                time.sleep(0.8)
                
                self.status_label.config(text="按下 ESC 鍵")
                send_key(SCAN_ESC); time.sleep(0.1); send_key(SCAN_ESC, True)
                time.sleep(0.5)
            else:
                self.status_label.config(text="未找到圖片 '01.png'，跳過步驟 11")
                time.sleep(1)
        except Exception as e:
            self.status_label.config(text=f"搜尋 '01.png' 發生錯誤: {e}")
            time.sleep(1)

        self.status_label.config(text="狀態: 執行完畢")
        self.is_running = False
        self.start_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = CustomApp(root)
    root.mainloop()
