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
# 終極自動化工具 V4.9 - 終極穩定整合版 (7秒等待 + 加速節奏 + 完整收尾)
# =================================================================
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
SCAN_ESC = 0x01
SCAN_X = 0x2D; SCAN_9 = 0x0A; SCAN_DOWN = 0x50; SCAN_ENTER = 0x1C; SCAN_I = 0x17; SCAN_ALT = 0x38
SCAN_7 = 0x08; SCAN_2 = 0x03; SCAN_5 = 0x06; SCAN_3 = 0x04
SCAN_INSERT = 0xD2
SW_RESTORE = 9
SW_MINIMIZE = 6

try:
    win32u = ctypes.WinDLL("win32u.dll", use_last_error=True)
    NtUserSendInput = win32u.NtUserSendInput
    NtUserSendInput.argtypes = (ctypes.c_ulong, ctypes.POINTER(INPUT), ctypes.c_int)
    NtUserSendInput.restype = ctypes.c_ulong
except:
    NtUserSendInput = None
user32 = ctypes.windll.user32
user32.GetCursorPos.argtypes = [ctypes.POINTER(POINT)]
user32.WindowFromPoint.argtypes = [POINT]
user32.WindowFromPoint.restype = ctypes.c_void_p
user32.ShowWindow.argtypes = [ctypes.c_void_p, ctypes.c_int]
user32.SetForegroundWindow.argtypes = [ctypes.c_void_p]

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

def mouse_left_click(clicks=1):
    for _ in range(clicks):
        mi_down = MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=MOUSEEVENTF_LEFTDOWN, time=0, dwExtraInfo=None)
        send_input(INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=mi_down)))
        time.sleep(random.uniform(0.05, 0.1))
        mi_up = MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=MOUSEEVENTF_LEFTUP, time=0, dwExtraInfo=None)
        send_input(INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=mi_up)))
        if clicks > 1: time.sleep(0.1)

def mouse_right_click(clicks=1):
    for _ in range(clicks):
        mi_down = MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=MOUSEEVENTF_RIGHTDOWN, time=0, dwExtraInfo=None)
        send_input(INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=mi_down)))
        time.sleep(random.uniform(0.05, 0.1))
        mi_up = MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=MOUSEEVENTF_RIGHTUP, time=0, dwExtraInfo=None)
        send_input(INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=mi_up)))
        if clicks > 1: time.sleep(0.1)

def mouse_drag(offset_x, offset_y):
    mi_down = MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=MOUSEEVENTF_LEFTDOWN, time=0, dwExtraInfo=None)
    send_input(INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=mi_down)))
    time.sleep(0.2)
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    move_mouse_to(pt.x + offset_x, pt.y + offset_y)
    time.sleep(0.2)
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
        self.root.title("終極自動化工具 V4.9")
        self.root.geometry("600x950")
        self.root.attributes("-topmost", True)
        self.is_running = False
        self.stop_event = threading.Event()
        self.current_task = "STORAGE"
        self.COLOR_SELECTED = "#2196F3"
        self.COLOR_NORMAL = "#E1E1E1"
       
        # 1. 任務選擇
        task_frame = tk.LabelFrame(root, text="任務選擇", font=("Arial", 10, "bold"), padx=10, pady=10)
        task_frame.pack(padx=10, pady=5, fill="x")
        self.btn_task_storage = tk.Button(task_frame, text="📦 倒數存倉", command=lambda: self.select_task("STORAGE"), width=25, height=2, bg=self.COLOR_SELECTED, fg="white")
        self.btn_task_storage.pack(side="left", padx=5, expand=True)
        self.btn_task_arrow = tk.Button(task_frame, text="🏹 製作箭流程", command=lambda: self.select_task("ARROW"), width=25, height=2, bg=self.COLOR_NORMAL, fg="black")
        self.btn_task_arrow.pack(side="left", padx=5, expand=True)
       
        # 2. 句柄管理
        hwnd_frame = tk.LabelFrame(root, text="句柄管理", font=("Arial", 10, "bold"), padx=10, pady=10)
        hwnd_frame.pack(padx=10, pady=5, fill="x")
        self.hwnd_entries = []
        for i in range(3):
            row = tk.Frame(hwnd_frame); row.pack(fill="x", pady=5)
            tk.Label(row, text=f"句柄 {chr(65+i)}:", width=8).pack(side="left")
            entry = tk.Entry(row, width=20); entry.pack(side="left", padx=5); self.hwnd_entries.append(entry)
            tk.Button(row, text=f"🔍 查詢視窗 {chr(65+i)}", command=lambda idx=i: self.start_get_hwnd(idx), bg="#9E9E9E", fg="white", width=15).pack(side="left")
       
        # 3. 執行參數
        param_frame = tk.LabelFrame(root, text="執行參數與項目勾選", font=("Arial", 10, "bold"), padx=10, pady=10)
        param_frame.pack(padx=10, pady=5, fill="x")
       
        row_time = tk.Frame(param_frame); row_time.pack(fill="x", pady=2)
        tk.Label(row_time, text="存倉間隔 (小時):", width=22, anchor="w").pack(side="left")
        self.interval_entry = tk.Entry(row_time, width=10); self.interval_entry.insert(0, "4"); self.interval_entry.pack(side="left", padx=5)
        row_time_arrow = tk.Frame(param_frame); row_time_arrow.pack(fill="x", pady=2)
        tk.Label(row_time_arrow, text="製作箭間隔 (分鐘):", width=22, anchor="w").pack(side="left")
        self.interval_arrow_entry = tk.Entry(row_time_arrow, width=10); self.interval_arrow_entry.insert(0, "5"); self.interval_arrow_entry.pack(side="left", padx=5)
       
        row_cycle = tk.Frame(param_frame); row_cycle.pack(fill="x", pady=2)
        tk.Label(row_cycle, text="執行次數 (0=無限):", width=22, anchor="w").pack(side="left")
        self.cycles_entry = tk.Entry(row_cycle, width=10); self.cycles_entry.insert(0, "0"); self.cycles_entry.pack(side="left", padx=5)
       
        tk.Frame(param_frame, height=2, bd=1, relief="sunken").pack(fill="x", pady=5)
       
        # 存倉項目勾選 (自定義次數)
        self.do_01 = tk.BooleanVar(value=True)
        row_01 = tk.Frame(param_frame); row_01.pack(fill="x", pady=2)
        tk.Checkbutton(row_01, text="執行裝備類", variable=self.do_01, font=("Arial", 9, "bold")).pack(side="left")
        tk.Label(row_01, text=" 次數:", width=10, anchor="w").pack(side="left")
        self.count_01_entry = tk.Entry(row_01, width=10); self.count_01_entry.insert(0, "20"); self.count_01_entry.pack(side="left", padx=5)
       
        self.do_02 = tk.BooleanVar(value=True)
        row_02 = tk.Frame(param_frame); row_02.pack(fill="x", pady=2)
        tk.Checkbutton(row_02, text="執行其他類", variable=self.do_02, font=("Arial", 9, "bold")).pack(side="left")
        tk.Label(row_02, text=" 次數:", width=10, anchor="w").pack(side="left")
        self.count_02_entry = tk.Entry(row_02, width=10); self.count_02_entry.insert(0, "6"); self.count_02_entry.pack(side="left", padx=5)
       
        self.do_qq = tk.BooleanVar(value=True)
        row_qq = tk.Frame(param_frame); row_qq.pack(fill="x", pady=2)
        tk.Checkbutton(row_qq, text="執行消耗類", variable=self.do_qq, font=("Arial", 9, "bold")).pack(side="left")
        tk.Label(row_qq, text=" 次數:", width=10, anchor="w").pack(side="left")
        self.count_qq_entry = tk.Entry(row_qq, width=10); self.count_qq_entry.insert(0, "5"); self.count_qq_entry.pack(side="left", padx=5)
       
        # 4. 狀態與按鈕
        self.status_label = tk.Label(root, text="狀態: 待機中", font=("Arial", 11), fg="blue", pady=5); self.status_label.pack()
        self.countdown_label = tk.Label(root, text="倒數: 00:00:00", font=("Arial", 11), fg="darkgreen"); self.countdown_label.pack()
        self.start_btn = tk.Button(root, text="▶ 開始執行", command=self.start, width=30, height=2, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")); self.start_btn.pack(pady=5)
        self.stop_btn = tk.Button(root, text="⏹ 強制停止", command=self.stop, width=30, height=2, bg="#F44336", fg="white", state="disabled"); self.stop_btn.pack(pady=5)

    def select_task(self, task):
        self.current_task = task
        if task == "STORAGE":
            self.btn_task_storage.config(bg=self.COLOR_SELECTED, fg="white")
            self.btn_task_arrow.config(bg=self.COLOR_NORMAL, fg="black")
        else:
            self.btn_task_arrow.config(bg=self.COLOR_SELECTED, fg="white")
            self.btn_task_storage.config(bg=self.COLOR_NORMAL, fg="black")

    def start_get_hwnd(self, index):
        threading.Thread(target=self.get_hwnd_countdown, args=(index,), daemon=True).start()

    def get_hwnd_countdown(self, index):
        self.hwnd_entries[index].config(state="disabled")
        for i in range(3, 0, -1):
            self.status_label.config(text=f"請移至視窗 {chr(65+index)}... {i}"); time.sleep(1)
        pt = POINT(); user32.GetCursorPos(ctypes.byref(pt))
        hwnd = user32.WindowFromPoint(pt)
        self.hwnd_entries[index].config(state="normal")
        self.hwnd_entries[index].delete(0, tk.END); self.hwnd_entries[index].insert(0, f"0x{hwnd:08X}")
        self.status_label.config(text=f"✓ 已獲取句柄: 0x{hwnd:08X}", fg="green")

    def find_img_path(self, img_name):
        base = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(".")
        return os.path.join(base, f"{img_name}.png")

    def find_and_click_v49(self, img, offset_x=0, offset_y=0, clicks=1, drag_x=0, drag_y=0):
        if self.stop_event.is_set(): return False
        try:
            path = self.find_img_path(img)
            loc = pyautogui.locateOnScreen(path, confidence=0.85)
            if loc:
                cx, cy = loc.left + loc.width // 2, loc.top + loc.height // 2
                move_mouse_to(cx + offset_x, cy + offset_y); time.sleep(0.2)
                if drag_x != 0 or drag_y != 0: mouse_drag(drag_x, drag_y)
                else: mouse_left_click(clicks)
                time.sleep(0.2); return True
            return False
        except: return False

    def task_storage_v49(self):
        # （此處保持你原本的內容不變）
        try:
            c1 = int(self.count_01_entry.get())
            c2 = int(self.count_02_entry.get())
            cq = int(self.count_qq_entry.get())
        except: c1, c2, cq = 20, 6, 5
        for i in range(3, 0, -1):
            if self.stop_event.is_set(): return False
            self.status_label.config(text=f"準備中... {i}"); time.sleep(1)
       
        send_key(SCAN_X); time.sleep(0.1); send_key(SCAN_X, True); time.sleep(1.0)
        send_key(SCAN_9); time.sleep(0.1); send_key(SCAN_9, True); time.sleep(0.5)
        send_key(SCAN_DOWN, False, True); time.sleep(0.1); send_key(SCAN_DOWN, True, True); time.sleep(0.5)
        for _ in range(2):
            if self.stop_event.is_set(): return False
            send_key(SCAN_ENTER); time.sleep(0.1); send_key(SCAN_ENTER, True); time.sleep(0.7)
        send_key(SCAN_I); time.sleep(0.1); send_key(SCAN_I, True); time.sleep(0.5)
       
        if self.do_01.get():
            path = self.find_img_path("01")
            loc = pyautogui.locateOnScreen(path, confidence=0.85)
            if loc:
                cx, cy = loc.left + loc.width // 2, loc.top + loc.height // 2
                move_mouse_to(cx, cy); time.sleep(0.2); mouse_left_click(); time.sleep(0.5)
                move_mouse_to(cx + 28, cy - 30); time.sleep(0.5)
                send_key(SCAN_ALT, False); time.sleep(0.2)
                for k in range(c1):
                    if self.stop_event.is_set(): send_key(SCAN_ALT, True); return False
                    self.status_label.config(text=f"存放裝備類: {k+1}/{c1}")
                    mouse_right_click(); time.sleep(0.6)
                send_key(SCAN_ALT, True); time.sleep(0.5)
           
        if self.do_02.get():
            path = self.find_img_path("01")
            loc = pyautogui.locateOnScreen(path, confidence=0.85)
            if loc:
                cx, cy = loc.left + loc.width // 2, loc.top + loc.height // 2
                move_mouse_to(cx, cy + 28); time.sleep(0.3); mouse_left_click(); time.sleep(0.5)
                move_mouse_to(cx + 60, cy - 32); time.sleep(0.5)
                send_key(SCAN_ALT, False); time.sleep(0.2)
                for k in range(c2):
                    if self.stop_event.is_set(): send_key(SCAN_ALT, True); return False
                    self.status_label.config(text=f"存放其他類: {k+1}/{c2}")
                    mouse_right_click(); time.sleep(0.6)
                send_key(SCAN_ALT, True); time.sleep(0.5)
        if self.do_qq.get():
            path = self.find_img_path("qq")
            loc = pyautogui.locateOnScreen(path, confidence=0.85)
            if loc:
                cx, cy = loc.left + loc.width // 2, loc.top + loc.height // 2
                move_mouse_to(cx, cy); time.sleep(0.2); mouse_left_click(); time.sleep(0.5)
                move_mouse_to(cx + 28, cy); time.sleep(0.5)
                send_key(SCAN_ALT, False); time.sleep(0.2)
                for k in range(cq):
                    if self.stop_event.is_set(): send_key(SCAN_ALT, True); return False
                    self.status_label.config(text=f"存放消耗類: {k+1}/{cq}")
                    mouse_right_click(); time.sleep(0.6)
                send_key(SCAN_ALT, True); time.sleep(0.5)
           
        send_key(SCAN_ESC); time.sleep(0.1); send_key(SCAN_ESC, True); time.sleep(0.5)
        self.find_and_click_v49("ca2")
        send_key(SCAN_X); time.sleep(0.1); send_key(SCAN_X, True)
        return True

    def task_arrow_v49(self):
        # === 修改 1：開始執行時先等待 3 秒 ===
        time.sleep(3)
        
        # 1. 開頭 Insert
        send_key(SCAN_INSERT, False, True); time.sleep(0.1); send_key(SCAN_INSERT, True, True); time.sleep(0.5)
       
        # 2. 採購大循環 (25次)
        for cycle in range(25):
            if self.stop_event.is_set(): return False
            self.status_label.config(text=f"採購循環: {cycle+1}/25")
            self.find_and_click_v49("buynpc")
            self.find_and_click_v49("buybuy")
            self.find_and_click_v49("dd", 0, -5, clicks=2)
            self.find_and_click_v49("ii", 0, -30, drag_x=300)
            self.find_and_click_v49("ff")
           
        # 3. 製作動作（共執行 25 次）
        for cycle in range(25):
            if self.stop_event.is_set(): return False
            self.status_label.config(text=f"製作動作: {cycle+1}/25")
            send_key(SCAN_7); time.sleep(0.1); send_key(SCAN_7, True)
            self.find_and_click_v49("gg", offset_y=-150, clicks=2)
        
        # === 修改 2：製作動作 25 次完成後等待 2 秒 ===
        time.sleep(2)
       
        # 4. 中段切換與成品轉移
        self.status_label.config(text="執行中段切換與確認...")
        self.find_and_click_v49("change")
        send_key(SCAN_ENTER); time.sleep(0.1); send_key(SCAN_ENTER, True); time.sleep(0.5)
        send_key(SCAN_DOWN, False, True); time.sleep(0.1); send_key(SCAN_DOWN, True, True); time.sleep(0.5)
        for _ in range(2): send_key(SCAN_ENTER); time.sleep(0.1); send_key(SCAN_ENTER, True); time.sleep(0.5)
       
        self.find_and_click_v49("hh", offset_y=60, drag_x=300)
       
        send_key(SCAN_3); time.sleep(0.1); send_key(SCAN_3, True); time.sleep(0.3)
        send_key(SCAN_5); time.sleep(0.1); send_key(SCAN_5, True); time.sleep(0.5)
        for _ in range(1): send_key(SCAN_ENTER); time.sleep(0.1); send_key(SCAN_ENTER, True); time.sleep(0.3)
       
        self.find_and_click_v49("over")
       
        # 5. 收尾追加流程
        self.status_label.config(text="執行收尾追加流程...")
        send_key(SCAN_9); time.sleep(0.1); send_key(SCAN_9, True); time.sleep(0.5)
        send_key(SCAN_DOWN, False, True); time.sleep(0.1); send_key(SCAN_DOWN, True, True); time.sleep(0.5)
        for _ in range(2): send_key(SCAN_ENTER); time.sleep(0.1); send_key(SCAN_ENTER, True); time.sleep(0.5)
        send_key(SCAN_I); time.sleep(0.1); send_key(SCAN_I, True); time.sleep(0.5)
       
        path_qq = self.find_img_path("qq")
        loc_qq = pyautogui.locateOnScreen(path_qq, confidence=0.85)
        if loc_qq:
            cx, cy = loc_qq.left + loc_qq.width // 2, loc_qq.top + loc_qq.height // 2
            move_mouse_to(cx, cy); time.sleep(0.3); mouse_left_click(1); time.sleep(0.3)
            move_mouse_to(cx + 28, cy); time.sleep(0.3)
            send_key(SCAN_ALT, False); time.sleep(0.2)
            mouse_right_click(1); time.sleep(0.5)
            send_key(SCAN_ALT, True); time.sleep(0.5)
           
        send_key(SCAN_ESC); time.sleep(0.1); send_key(SCAN_ESC, True); time.sleep(0.5)
        self.find_and_click_v49("ca2")
        send_key(SCAN_INSERT, False, True); time.sleep(0.1); send_key(SCAN_INSERT, True, True); time.sleep(0.5)
       
        return True

    def start(self):
        try:
            self.interval_storage = float(self.interval_entry.get())
            self.interval_arrow = float(self.interval_arrow_entry.get())
            self.total_cycles = int(self.cycles_entry.get())
        except: messagebox.showerror("錯誤", "請輸入有效數字"); return
        hwnds = []
        for i, e in enumerate(self.hwnd_entries):
            val = e.get().strip()
            if val: hwnds.append((i, int(val, 16) if val.lower().startswith("0x") else int(val)))
        if not hwnds: messagebox.showerror("錯誤", "至少需一個句柄"); return
        self.is_running = True; self.stop_event.clear()
        self.start_btn.config(state="disabled"); self.stop_btn.config(state="normal")
        threading.Thread(target=self.run_loop, args=(hwnds,), daemon=True).start()

    def stop(self):
        self.stop_event.set(); self.is_running = False
        self.status_label.config(text="狀態: 已停止", fg="red")
        self.start_btn.config(state="normal"); self.stop_btn.config(state="disabled")

    def run_loop(self, hwnds):
        cycle = 0
        while not self.stop_event.is_set():
            if self.total_cycles > 0 and cycle >= self.total_cycles: break
            cycle += 1
            for idx, hwnd in hwnds:
                if self.stop_event.is_set(): break
                user32.ShowWindow(hwnd, SW_RESTORE); time.sleep(0.2); user32.SetForegroundWindow(hwnd); time.sleep(0.5)
                if self.current_task == "STORAGE": self.task_storage_v49()
                else: self.task_arrow_v49()
                user32.ShowWindow(hwnd, SW_MINIMIZE); time.sleep(0.5)
            if self.stop_event.is_set(): break
           
            wait = int(self.interval_storage * 3600) if self.current_task == "STORAGE" else int(self.interval_arrow * 60)
            while wait > 0 and not self.stop_event.is_set():
                h, r = divmod(wait, 3600); m, s = divmod(r, 60)
                self.countdown_label.config(text=f"倒數: {h:02}:{m:02}:{s:02}"); time.sleep(1); wait -= 1
        self.stop()

if __name__ == "__main__":
    root = tk.Tk(); app = CustomApp(root); root.mainloop()
