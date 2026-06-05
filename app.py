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
# 終極自動化工具 V3.8 - 任務切換版 (恢復 0.5s 穩定延遲)
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
SCAN_7 = 0x08; SCAN_2 = 0x03; SCAN_5 = 0x06

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
        self.root.title("終極自動化工具 V3.8")
        self.root.geometry("600x800")
        self.root.attributes("-topmost", True)
        self.is_running = False
        self.stop_event = threading.Event()
        self.current_task = "STORAGE"
        self.COLOR_SELECTED = "#2196F3"
        self.COLOR_NORMAL = "#E1E1E1"
        
        task_frame = tk.LabelFrame(root, text="任務選擇", font=("Arial", 10, "bold"), padx=10, pady=10)
        task_frame.pack(padx=10, pady=10, fill="x")
        self.btn_task_storage = tk.Button(task_frame, text="📦 倒數存倉 (1-13步)", command=lambda: self.select_task("STORAGE"), width=25, height=2, bg=self.COLOR_SELECTED, fg="white")
        self.btn_task_storage.pack(side="left", padx=5, expand=True)
        self.btn_task_arrow = tk.Button(task_frame, text="🏹 製作箭流程", command=lambda: self.select_task("ARROW"), width=25, height=2, bg=self.COLOR_NORMAL, fg="black")
        self.btn_task_arrow.pack(side="left", padx=5, expand=True)
        
        hwnd_frame = tk.LabelFrame(root, text="句柄管理", font=("Arial", 10, "bold"), padx=10, pady=10)
        hwnd_frame.pack(padx=10, pady=10, fill="x")
        self.hwnd_entries = []
        for i in range(3):
            row = tk.Frame(hwnd_frame); row.pack(fill="x", pady=5)
            tk.Label(row, text=f"句柄 {chr(65+i)}:", width=8).pack(side="left")
            entry = tk.Entry(row, width=20); entry.pack(side="left", padx=5); self.hwnd_entries.append(entry)
            tk.Button(row, text=f"🔍 查詢視窗 {chr(65+i)}", command=lambda idx=i: self.start_get_hwnd(idx), bg="#9E9E9E", fg="white", width=15).pack(side="left")
        
        param_frame = tk.LabelFrame(root, text="執行參數", font=("Arial", 10, "bold"), padx=10, pady=10)
        param_frame.pack(padx=10, pady=10, fill="x")
        row1 = tk.Frame(param_frame); row1.pack(fill="x", pady=5)
        tk.Label(row1, text="循環間隔 (小時):", width=15).pack(side="left")
        self.interval_entry = tk.Entry(row1, width=10); self.interval_entry.insert(0, "4"); self.interval_entry.pack(side="left", padx=5)
        row2 = tk.Frame(param_frame); row2.pack(fill="x", pady=5)
        tk.Label(row2, text="執行次數 (0=無限):", width=15).pack(side="left")
        self.cycles_entry = tk.Entry(row2, width=10); self.cycles_entry.insert(0, "0"); self.cycles_entry.pack(side="left", padx=5)
        
        self.status_label = tk.Label(root, text="狀態: 待機中", font=("Arial", 11), fg="blue", pady=10); self.status_label.pack()
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

    def find_and_click_v30(self, img_name, offset_x=0, offset_y=0, click_center=True):
        if self.stop_event.is_set(): return False
        try:
            base = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(".")
            path = os.path.join(base, f"{img_name}.png") if not img_name.endswith(".png") else os.path.join(base, img_name)
            loc = pyautogui.locateOnScreen(path, confidence=0.85)
            if loc:
                cx, cy = loc.left + loc.width // 2, loc.top + loc.height // 2
                if click_center:
                    move_mouse_to(cx, cy); time.sleep(0.2); mouse_left_click(); time.sleep(0.5)
                move_mouse_to(cx + offset_x, cy + offset_y); time.sleep(0.5)
                return True
            return False
        except: return False

    def find_and_click_v33(self, img, offset_x=0, offset_y=0, clicks=1, drag_x=0, drag_y=0):
        if self.stop_event.is_set(): return False
        try:
            base = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(".")
            path = os.path.join(base, f"{img}.png")
            loc = pyautogui.locateOnScreen(path, confidence=0.85)
            if loc:
                cx, cy = loc.left + loc.width // 2, loc.top + loc.height // 2
                move_mouse_to(cx + offset_x, cy + offset_y); time.sleep(0.2)
                if drag_x != 0 or drag_y != 0: mouse_drag(drag_x, drag_y)
                else: mouse_left_click(clicks)
                time.sleep(0.5); return True
            return False
        except: return False

    def task_storage_v30(self):
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
        if self.find_and_click_v30("01.png", 28, -30):
            send_key(SCAN_ALT, False); time.sleep(0.2)
            for k in range(20):
                if self.stop_event.is_set(): send_key(SCAN_ALT, True); return False
                self.status_label.config(text=f"右鍵點擊 (01): {k+1}/20")
                mouse_right_click(); time.sleep(0.6)
            send_key(SCAN_ALT, True); time.sleep(0.5)
        if self.find_and_click_v30("02.png", 28, -60):
            send_key(SCAN_ALT, False); time.sleep(0.2)
            for k in range(6):
                if self.stop_event.is_set(): send_key(SCAN_ALT, True); return False
                self.status_label.config(text=f"右鍵點擊 (02): {k+1}/6")
                mouse_right_click(); time.sleep(0.6)
            send_key(SCAN_ALT, True); time.sleep(0.5)
        send_key(SCAN_ESC); time.sleep(0.1); send_key(SCAN_ESC, True); time.sleep(0.5)
        self.find_and_click_v33("ca2")
        send_key(SCAN_X); time.sleep(0.1); send_key(SCAN_X, True)
        return True

    def task_arrow_v38(self):
        for cycle in range(25):
            if self.stop_event.is_set(): return False
            self.status_label.config(text=f"製作箭大循環: {cycle+1}/25")
            if not self.find_and_click_v33("buynpc"): return False
            if not self.find_and_click_v33("buybuy"): return False
            if not self.find_and_click_v33("dd", 0, -5, clicks=2): return False
            if not self.find_and_click_v33("ii", 0, -30, drag_x=300): return False
            if not self.find_and_click_v33("ff"): return False
            
        for cycle in range(25):
            if self.stop_event.is_set(): return False
            self.status_label.config(text=f"強化動作: {cycle+1}/25")
            # 🌟 調整處：恢復 0.5 秒穩定延遲
            send_key(SCAN_7); time.sleep(0.1); send_key(SCAN_7, True); time.sleep(0.5)
            if not self.find_and_click_v33("ee", clicks=2): break
            time.sleep(0.5)
            
        if not self.find_and_click_v33("change"): return False
        send_key(SCAN_ENTER); time.sleep(0.1); send_key(SCAN_ENTER, True); time.sleep(0.5)
        send_key(SCAN_DOWN, False, True); time.sleep(0.1); send_key(SCAN_DOWN, True, True); time.sleep(0.5)
        for _ in range(2): send_key(SCAN_ENTER); time.sleep(0.1); send_key(SCAN_ENTER, True); time.sleep(0.5)
        if not self.find_and_click_v33("hh", drag_x=300): return False
        send_key(SCAN_2); time.sleep(0.1); send_key(SCAN_2, True); time.sleep(0.3)
        send_key(SCAN_5); time.sleep(0.1); send_key(SCAN_5, True); time.sleep(0.5)
        for _ in range(2): send_key(SCAN_ENTER); time.sleep(0.1); send_key(SCAN_ENTER, True); time.sleep(0.3)
        if not self.find_and_click_v33("over"): return False
        return True

    def start(self):
        try:
            self.interval = float(self.interval_entry.get())
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
                success = self.task_storage_v30() if self.current_task == "STORAGE" else self.task_arrow_v38()
                if not success: break
                user32.ShowWindow(hwnd, SW_MINIMIZE); time.sleep(0.5)
            if self.stop_event.is_set(): break
            wait = int(self.interval * 3600)
            while wait > 0 and not self.stop_event.is_set():
                h, r = divmod(wait, 3600); m, s = divmod(r, 60)
                self.countdown_label.config(text=f"倒數: {h:02}:{m:02}:{s:02}"); time.sleep(1); wait -= 1
        self.stop()

if __name__ == "__main__":
    root = tk.Tk(); app = CustomApp(root); root.mainloop()
