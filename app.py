import tkinter as tk
from tkinter import messagebox
import time
import threading
import ctypes
import random
import sys
import pyautogui
import os

# =================================================================
# 終極自動化工具 V3.0：多句柄支援 + 自定義計時 + 防呆機制
# =================================================================

# ==================== Windows API 結構定義 ====================
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

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

# ==================== 常數定義 ====================
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_EXTENDEDKEY = 0x0001
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010

# 掃描碼定義
SCAN_ESC = 0x01
SCAN_X = 0x2D
SCAN_9 = 0x0A
SCAN_DOWN = 0x50
SCAN_ENTER = 0x1C
SCAN_I = 0x17
SCAN_ALT = 0x38

# 視窗顯示常數
SW_RESTORE = 9
SW_MINIMIZE = 6

# ==================== 初始化 Windows API ====================
try:
    win32u = ctypes.WinDLL("win32u.dll", use_last_error=True)
    NtUserSendInput = win32u.NtUserSendInput
    NtUserSendInput.argtypes = (ctypes.c_ulong, ctypes.POINTER(INPUT), ctypes.c_int)
    NtUserSendInput.restype = ctypes.c_ulong
except:
    NtUserSendInput = None

user32 = ctypes.windll.user32

# 設定 API 參數類型
user32.GetCursorPos.argtypes = [ctypes.POINTER(POINT)]
user32.WindowFromPoint.argtypes = [POINT]
user32.WindowFromPoint.restype = ctypes.c_void_p
user32.ShowWindow.argtypes = [ctypes.c_void_p, ctypes.c_int]
user32.SetForegroundWindow.argtypes = [ctypes.c_void_p]

# ==================== 輸入函數 ====================
def send_input(ii):
    if NtUserSendInput:
        NtUserSendInput(1, ctypes.byref(ii), ctypes.sizeof(ii))
    else:
        user32.SendInput(1, ctypes.byref(ii), ctypes.sizeof(ii))

def move_mouse_to(x, y):
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    nx = int(x * 65536 / width)
    ny = int(y * 65536 / height)
    mi = MOUSEINPUT(dx=nx, dy=ny, mouseData=0, dwFlags=MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, time=0, dwExtraInfo=None)
    send_input(INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=mi)))

def mouse_left_click():
    mi_down = MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=MOUSEEVENTF_LEFTDOWN, time=0, dwExtraInfo=None)
    send_input(INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=mi_down)))
    time.sleep(random.uniform(0.05, 0.1))
    mi_up = MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=MOUSEEVENTF_LEFTUP, time=0, dwExtraInfo=None)
    send_input(INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=mi_up)))

def mouse_right_click():
    mi_down = MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=MOUSEEVENTF_RIGHTDOWN, time=0, dwExtraInfo=None)
    send_input(INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=mi_down)))
    time.sleep(random.uniform(0.05, 0.1))
    mi_up = MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=MOUSEEVENTF_RIGHTUP, time=0, dwExtraInfo=None)
    send_input(INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=mi_up)))

def send_key(scancode, is_up=False, is_extended=False):
    flags = KEYEVENTF_SCANCODE
    if is_up: flags |= KEYEVENTF_KEYUP
    if is_extended: flags |= KEYEVENTF_EXTENDEDKEY
    ki = KEYBDINPUT(wVk=0, wScan=scancode, dwFlags=flags, time=0, dwExtraInfo=None)
    send_input(INPUT(type=INPUT_KEYBOARD, union=INPUT_UNION(ki=ki)))

# ==================== 主應用程式類別 ====================
class CustomApp:
    # 單次執行耗時（秒）- 根據您的 1-13 步流程計算
    SINGLE_EXECUTION_TIME = 32  # 約 32 秒

    def __init__(self, root):
        self.root = root
        self.root.title("終極自動化工具 V3.0 - 多句柄 + 自定義計時")
        self.root.geometry("600x750")
        self.root.attributes("-topmost", True)
        
        self.is_running = False
        self.stop_event = threading.Event()
        
        # 句柄存儲
        self.hwnd_list = [None, None, None]  # 支援最多 3 個句柄
        self.current_cycle = 0
        self.total_cycles = 0
        self.cycle_interval_hours = 4.0
        
        # ==================== UI 佈局 ====================
        
        # 標題
        tk.Label(root, text="終極自動化工具 V3.0", font=("Arial", 14, "bold")).pack(pady=10)
        
        # ==================== 句柄管理區 ====================
        hwnd_frame = tk.LabelFrame(root, text="句柄管理 (支援最多 3 個視窗)", font=("Arial", 10, "bold"), padx=10, pady=10)
        hwnd_frame.pack(padx=10, pady=10, fill="x")
        
        self.hwnd_entries = []
        for i in range(3):
            row_frame = tk.Frame(hwnd_frame)
            row_frame.pack(fill="x", pady=5)
            
            tk.Label(row_frame, text=f"句柄 {chr(65+i)}:", font=("Arial", 10), width=8).pack(side="left")
            entry = tk.Entry(row_frame, width=20, font=("Arial", 10))
            entry.pack(side="left", padx=5)
            self.hwnd_entries.append(entry)
            
            btn = tk.Button(row_frame, text=f"🔍 查詢視窗 {chr(65+i)}", command=lambda idx=i: self.start_get_hwnd(idx), bg="#2196F3", fg="white", width=18)
            btn.pack(side="left", padx=5)
        
        # ==================== 參數設定區 ====================
        param_frame = tk.LabelFrame(root, text="執行參數設定", font=("Arial", 10, "bold"), padx=10, pady=10)
        param_frame.pack(padx=10, pady=10, fill="x")
        
        # 循環間隔
        interval_row = tk.Frame(param_frame)
        interval_row.pack(fill="x", pady=5)
        tk.Label(interval_row, text="循環間隔 (小時):", font=("Arial", 10), width=15).pack(side="left")
        self.interval_entry = tk.Entry(interval_row, width=10, font=("Arial", 10))
        self.interval_entry.insert(0, "4")
        self.interval_entry.pack(side="left", padx=5)
        tk.Label(interval_row, text="(輸入 0.1 = 6 分鐘)", font=("Arial", 9), fg="gray").pack(side="left")
        
        # 執行次數
        cycles_row = tk.Frame(param_frame)
        cycles_row.pack(fill="x", pady=5)
        tk.Label(cycles_row, text="執行次數:", font=("Arial", 10), width=15).pack(side="left")
        self.cycles_entry = tk.Entry(cycles_row, width=10, font=("Arial", 10))
        self.cycles_entry.insert(0, "0")
        self.cycles_entry.pack(side="left", padx=5)
        tk.Label(cycles_row, text="(0 = 無限循環)", font=("Arial", 9), fg="gray").pack(side="left")
        
        # ==================== 狀態顯示區 ====================
        status_frame = tk.LabelFrame(root, text="狀態顯示", font=("Arial", 10, "bold"), padx=10, pady=10)
        status_frame.pack(padx=10, pady=10, fill="x")
        
        self.cycle_label = tk.Label(status_frame, text="循環: 0/0", font=("Arial", 11), fg="purple")
        self.cycle_label.pack(pady=5)
        
        self.execution_time_label = tk.Label(status_frame, text="預計耗時: 計算中...", font=("Arial", 10), fg="darkblue")
        self.execution_time_label.pack(pady=5)
        
        self.countdown_label = tk.Label(status_frame, text="倒數: 00:00:00", font=("Arial", 11), fg="darkgreen")
        self.countdown_label.pack(pady=5)
        
        self.status_label = tk.Label(status_frame, text="狀態: 待機中", font=("Arial", 11), fg="blue")
        self.status_label.pack(pady=20)
        
        # ==================== 控制按鈕區 ====================
        button_frame = tk.Frame(root)
        button_frame.pack(padx=10, pady=10, fill="x")
        
        self.start_btn = tk.Button(button_frame, text="▶ 開始全流程 (1-13步)", command=self.start, width=25, height=2, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.start_btn.pack(pady=5)
        
        self.stop_btn = tk.Button(button_frame, text="⏹ 強制停止所有動作", command=self.stop, width=25, height=2, bg="#F44336", fg="white", font=("Arial", 10, "bold"), state="disabled")
        self.stop_btn.pack(pady=5)

    # ==================== 句柄查詢功能 ====================
    def start_get_hwnd(self, index):
        """啟動句柄查詢倒數"""
        threading.Thread(target=self.get_hwnd_countdown, args=(index,), daemon=True).start()

    def get_hwnd_countdown(self, index):
        """倒數 3 秒後自動抓取滑鼠所在視窗的句柄"""
        self.hwnd_entries[index].config(state="disabled")
        for i in range(3, 0, -1):
            self.status_label.config(text=f"請將滑鼠移至視窗 {chr(65+index)}... {i}", fg="orange")
            time.sleep(1)
        
        # 獲取滑鼠所在座標
        pt = POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        # 獲取該座標的視窗句柄
        hwnd = user32.WindowFromPoint(pt)
        
        # 將句柄轉為 16 進位顯示在輸入框中
        self.hwnd_entries[index].delete(0, tk.END)
        self.hwnd_entries[index].insert(0, f"0x{hwnd:08X}")
        self.hwnd_list[index] = hwnd
        
        self.status_label.config(text=f"✓ 已成功獲取句柄 {chr(65+index)}: 0x{hwnd:08X}", fg="green")
        self.hwnd_entries[index].config(state="normal")

    # ==================== 視窗控制功能 ====================
    def bring_to_foreground(self, hwnd):
        """將指定視窗置頂並激活"""
        if not hwnd:
            return False
        try:
            # 還原視窗（如果被最小化）
            user32.ShowWindow(hwnd, SW_RESTORE)
            time.sleep(0.2)
            # 將視窗帶到最前景
            user32.SetForegroundWindow(hwnd)
            time.sleep(0.5)
            return True
        except Exception as e:
            self.status_label.config(text=f"置頂視窗失敗: {e}", fg="red")
            return False

    def minimize_window(self, hwnd):
        """將指定視窗最小化"""
        if not hwnd:
            return False
        try:
            user32.ShowWindow(hwnd, SW_MINIMIZE)
            time.sleep(0.2)
            return True
        except:
            return False

    # ==================== 自動化執行功能 ====================
    def find_and_click_with_offset(self, img_name, offset_x=0, offset_y=0, click_center=True):
        """搜尋圖片並點擊（保留原本邏輯）"""
        if self.stop_event.is_set():
            return False
        try:
            base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(".")
            image_path = os.path.join(base_path, img_name)
            location = pyautogui.locateOnScreen(image_path, confidence=0.85)
            if location:
                cx = location.left + location.width // 2
                cy = location.top + location.height // 2
                if click_center:
                    move_mouse_to(cx, cy)
                    time.sleep(0.2)
                    mouse_left_click()
                    time.sleep(0.5)
                
                target_x = cx + offset_x
                target_y = cy + offset_y
                move_mouse_to(target_x, target_y)
                time.sleep(0.5)
                return True
            return False
        except:
            return False

    def execute_automation_steps(self):
        """執行 1-13 步自動化流程（保留原本邏輯）"""
        # 1. 倒數 3 秒
        for i in range(3, 0, -1):
            if self.stop_event.is_set():
                return False
            self.status_label.config(text=f"準備就緒... {i}")
            time.sleep(1)
        
        # 2-6 步: 基礎按鍵
        self.status_label.config(text="執行: 步驟 2-6 (按鍵序列)")
        if self.stop_event.is_set():
            return False
        send_key(SCAN_X); time.sleep(0.1); send_key(SCAN_X, True); time.sleep(1.0)
        if self.stop_event.is_set():
            return False
        send_key(SCAN_9); time.sleep(0.1); send_key(SCAN_9, True); time.sleep(0.5)
        if self.stop_event.is_set():
            return False
        send_key(SCAN_DOWN, False, True); time.sleep(0.1); send_key(SCAN_DOWN, True, True); time.sleep(0.5)
        if self.stop_event.is_set():
            return False
        for _ in range(2):
            if self.stop_event.is_set():
                return False
            send_key(SCAN_ENTER); time.sleep(0.1); send_key(SCAN_ENTER, True); time.sleep(0.7)
        if self.stop_event.is_set():
            return False
        send_key(SCAN_I); time.sleep(0.1); send_key(SCAN_I, True); time.sleep(0.5)
        
        # 7-8 步: 搜尋 01.png 並偏移 + Alt右鍵 20次
        self.status_label.config(text="執行: 步驟 7-8 (01.png 偏移)")
        if self.stop_event.is_set():
            return False
        if self.find_and_click_with_offset("01.png", 28, -30):
            if self.stop_event.is_set():
                return False
            send_key(SCAN_ALT, False); time.sleep(0.2)
            for k in range(20):
                if self.stop_event.is_set():
                    send_key(SCAN_ALT, True)
                    return False
                self.status_label.config(text=f"右鍵點擊 (01): {k+1}/20")
                mouse_right_click(); time.sleep(0.6)
            send_key(SCAN_ALT, True); time.sleep(0.5)
        else:
            self.status_label.config(text="錯誤: 未找到 01.png，跳過步驟 7-8", fg="orange")
        
        # 9-10 步: 搜尋 02.png 並偏移 + Alt右鍵 6次
        self.status_label.config(text="執行: 步驟 9-10 (02.png 偏移)")
        if self.stop_event.is_set():
            return False
        if self.find_and_click_with_offset("02.png", 28, -60):
            if self.stop_event.is_set():
                return False
            send_key(SCAN_ALT, False); time.sleep(0.2)
            for k in range(6):
                if self.stop_event.is_set():
                    send_key(SCAN_ALT, True)
                    return False
                self.status_label.config(text=f"右鍵點擊 (02): {k+1}/6")
                mouse_right_click(); time.sleep(0.6)
            send_key(SCAN_ALT, True); time.sleep(0.5)
        else:
            self.status_label.config(text="錯誤: 未找到 02.png，跳過步驟 9-10", fg="orange")
        
        # 11 步: 按下 Esc
        self.status_label.config(text="執行: 步驟 11 (Esc)")
        if self.stop_event.is_set():
            return False
        send_key(SCAN_ESC); time.sleep(0.1); send_key(SCAN_ESC, True); time.sleep(0.5)
        
        # 12 步: 搜尋 ca2.png 並點擊
        self.status_label.config(text="執行: 步驟 12 (ca2.png)")
        if self.stop_event.is_set():
            return False
        if not self.find_and_click_with_offset("ca2.png", 0, 0, click_center=True):
            self.status_label.config(text="錯誤: 未找到 ca2.png，跳過步驟 12", fg="orange")
        time.sleep(0.5)
        
        # 13 步: 按下 X
        self.status_label.config(text="執行: 步驟 13 (X)")
        if self.stop_event.is_set():
            return False
        send_key(SCAN_X); time.sleep(0.1); send_key(SCAN_X, True)
        
        return True

    # ==================== 排程與循環控制 ====================
    def start(self):
        """開始執行"""
        if self.is_running:
            return
        
        # 驗證輸入
        try:
            interval_str = self.interval_entry.get().strip()
            cycles_str = self.cycles_entry.get().strip()
            
            if not interval_str or not cycles_str:
                messagebox.showerror("輸入錯誤", "請填寫循環間隔和執行次數")
                return
            
            self.cycle_interval_hours = float(interval_str)
            self.total_cycles = int(cycles_str)
            
            if self.cycle_interval_hours <= 0:
                messagebox.showerror("輸入錯誤", "循環間隔必須大於 0")
                return
            
            if self.total_cycles < 0:
                messagebox.showerror("輸入錯誤", "執行次數不能為負數")
                return
            
        except ValueError:
            messagebox.showerror("輸入錯誤", "請輸入有效的數字")
            return
        
        # 讀取句柄
        active_hwnds = []
        for i, entry in enumerate(self.hwnd_entries):
            hwnd_str = entry.get().strip()
            if hwnd_str:
                try:
                    hwnd = int(hwnd_str, 16) if hwnd_str.lower().startswith("0x") else int(hwnd_str)
                    if hwnd:
                        active_hwnds.append((i, hwnd))
                except ValueError:
                    messagebox.showerror("句柄錯誤", f"句柄 {chr(65+i)} 格式無效")
                    return
        
        if not active_hwnds:
            messagebox.showerror("句柄錯誤", "至少需要設定一個句柄")
            return
        
        # 計算總耗時
        total_execution_time = self.SINGLE_EXECUTION_TIME * len(active_hwnds)
        interval_seconds = self.cycle_interval_hours * 3600
        
        # 防呆檢查：間隔時間是否足夠
        if interval_seconds < total_execution_time:
            messagebox.showerror(
                "設定錯誤",
                f"循環間隔過短！\n\n"
                f"您設定的間隔: {self.cycle_interval_hours} 小時 ({interval_seconds:.0f} 秒)\n"
                f"預計執行耗時: {total_execution_time} 秒 ({total_execution_time/60:.1f} 分鐘)\n\n"
                f"請重新輸入大於 {total_execution_time/3600:.2f} 小時的間隔"
            )
            return
        
        # 開始執行
        self.is_running = True
        self.stop_event.clear()
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.current_cycle = 0
        
        # 更新顯示
        cycles_display = f"{self.total_cycles}" if self.total_cycles > 0 else "∞"
        self.cycle_label.config(text=f"循環: 0/{cycles_display}")
        self.execution_time_label.config(text=f"預計耗時: {total_execution_time} 秒 ({total_execution_time/60:.1f} 分鐘)")
        
        # 啟動排程執行緒
        threading.Thread(target=self.schedule_run, args=(active_hwnds,), daemon=True).start()

    def stop(self):
        """強制停止"""
        self.stop_event.set()
        self.is_running = False
        self.status_label.config(text="狀態: 已強制停止", fg="red")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.countdown_label.config(text="倒數: 00:00:00")

    def schedule_run(self, active_hwnds):
        """排程執行邏輯"""
        self.status_label.config(text="狀態: 排程啟動中...", fg="blue")
        
        cycle = 0
        while True:
            # 檢查停止事件
            if self.stop_event.is_set():
                break
            
            # 檢查循環次數限制
            if self.total_cycles > 0 and cycle >= self.total_cycles:
                break
            
            cycle += 1
            self.current_cycle = cycle
            cycles_display = f"{self.total_cycles}" if self.total_cycles > 0 else "∞"
            self.cycle_label.config(text=f"循環: {self.current_cycle}/{cycles_display}")
            
            # 執行所有活躍的視窗
            for window_index, hwnd in active_hwnds:
                if self.stop_event.is_set():
                    break
                
                self.status_label.config(text=f"狀態: 執行第 {self.current_cycle} 次循環 - 視窗 {chr(65+window_index)}", fg="blue")
                
                # 置頂視窗
                if not self.bring_to_foreground(hwnd):
                    self.status_label.config(text=f"錯誤: 無法置頂視窗 {chr(65+window_index)}", fg="red")
                    continue
                
                # 執行自動化步驟
                if not self.execute_automation_steps():
                    self.status_label.config(text=f"狀態: 第 {self.current_cycle} 次循環被中止", fg="red")
                    break
                
                # 最小化視窗
                self.minimize_window(hwnd)
                time.sleep(0.5)
            
            # 檢查是否需要繼續
            if self.stop_event.is_set():
                break
            
            # 檢查是否是最後一個循環
            if self.total_cycles > 0 and cycle >= self.total_cycles:
                self.status_label.config(text="狀態: 所有循環執行完畢", fg="green")
                break
            
            # 倒數等待
            self.status_label.config(text=f"狀態: 第 {self.current_cycle} 次循環完成，等待下次執行...", fg="darkgreen")
            remaining_time = int(self.cycle_interval_hours * 3600)
            
            while remaining_time > 0 and not self.stop_event.is_set():
                hours, remainder = divmod(remaining_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                self.countdown_label.config(text=f"倒數: {hours:02}:{minutes:02}:{seconds:02}")
                time.sleep(1)
                remaining_time -= 1
            
            if self.stop_event.is_set():
                self.status_label.config(text="狀態: 排程已停止", fg="red")
                break
        
        # 執行完畢，重置按鈕
        self.is_running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.countdown_label.config(text="倒數: 00:00:00")

# ==================== 主程式入口 ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = CustomApp(root)
    root.mainloop()
