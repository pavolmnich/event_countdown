import tkinter as tk
from tkinter import ttk
from datetime import datetime
import time
import json
import os
from screeninfo import get_monitors

# --- KONŠTANTY ---
FONT_SIZE_TIME = 62
FONT_SIZE_EVENT = 48
FONT_SIZE_COUNTDOWN = 80
COLOR_BG = "#222"
COLOR_FG = "#fff"
COLOR_COUNTDOWN_FG = "#ff5555"
COLOR_FG_SECONDARY = "#888"
COLOR_BTN_BG = "#222"
COLOR_BTN_FG = "#888"
COLOR_BTN_ACTIVE_BG = "#222"
COLOR_BTN_ACTIVE_FG = "#fff"
FILE_NAME = "intervals.json"

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("Helvetica", 12))
        label.pack(ipadx=8, ipady=4)

    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

class EventCountdown(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Odpočítavanie koncertov")
        self.geometry("800x600")
        self.configure(bg="#f0f0f0")

        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12), padding=5)
        style.configure("TEntry", font=("Helvetica", 12), padding=5)
        style.configure("TButton", font=("Helvetica", 12), padding=5)

        # Event name frame
        self.name_frame = ttk.Frame(self)
        self.name_frame.pack(pady=10)
        ttk.Label(self.name_frame, text="Interpret:").pack(side=tk.LEFT)
        self.event_name = ttk.Entry(self.name_frame, width=30)
        self.event_name.pack(side=tk.LEFT, padx=5)

        # DateTime frame
        self.datetime_frame = ttk.Frame(self)
        self.datetime_frame.pack(pady=10)
        ttk.Label(self.datetime_frame, text="Dátum (DD.MM.YYYY):").pack(side=tk.LEFT)
        self.date_entry = ttk.Entry(self.datetime_frame, width=15)
        self.date_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(self.datetime_frame, text="Čas (HH:MM):").pack(side=tk.LEFT)
        self.time_entry = ttk.Entry(self.datetime_frame, width=10)
        self.time_entry.pack(side=tk.LEFT, padx=5)

        # Add interval button
        self.add_button = ttk.Button(self, text="Pridať interval", command=self.add_interval)
        self.add_button.pack(pady=5)

        # List of intervals
        self.intervals = []  # List of dicts: {name, datetime}
        self.intervals_frame = ttk.Frame(self)
        self.intervals_frame.pack(pady=10)
        self.intervals_listbox = tk.Listbox(self.intervals_frame, width=60, height=6, font=("Helvetica", 12))
        self.intervals_listbox.pack(side=tk.LEFT, padx=5)
        self.scrollbar = ttk.Scrollbar(self.intervals_frame, orient="vertical", command=self.intervals_listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.intervals_listbox.config(yscrollcommand=self.scrollbar.set)

        # Load from file button
        self.load_button = ttk.Button(self, text="Načítať intervaly zo súboru", command=self.load_intervals_from_file)
        self.load_button.pack(pady=5)

        # Start button
        self.start_button = ttk.Button(self, text="Spustiť odpočítavanie", command=self.start_countdown)
        self.start_button.pack(pady=10)

        self.event_label = ttk.Label(
            self,
            text="Zadajte údaje o koncerte a pridajte intervaly",
            font=("Helvetica", 14)
        )
        self.event_label.pack(pady=10)

        self.is_counting = False
        self.target_datetime = None
        self.current_interval_index = None

        # Načítaj intervaly zo súboru až po vytvorení všetkých widgetov
        self.load_intervals_from_file()
        # Ak sa podarilo načítať aspoň jeden interval, automaticky otvor odpočítavanie a skry úvodné okno
        if self.intervals:
            # Vyber najbližší interval
            now = datetime.now()
            future_intervals = [iv for iv in self.intervals if iv["datetime"] > now]
            if future_intervals:
                future_intervals.sort(key=lambda x: x["datetime"])
                self.current_interval_index = self.intervals.index(future_intervals[0])
                self.target_datetime = future_intervals[0]["datetime"]
                self.is_counting = True
                self.withdraw()
                self.open_countdown_window(future_intervals[0]["name"])

    def add_interval(self):
        date_str = self.date_entry.get()
        time_str = self.time_entry.get()
        event_name = self.event_name.get()
        if not all([date_str, time_str, event_name]):
            self.event_label.config(text="Prosím vyplňte všetky údaje!")
            return
        try:
            dt = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
            if dt <= datetime.now():
                self.event_label.config(text="Zadajte budúci dátum a čas!")
                return
            self.intervals.append({"name": event_name, "datetime": dt})
            self.update_intervals_listbox()
            self.event_label.config(text="Interval pridaný.")
            self.event_name.delete(0, tk.END)
            self.date_entry.delete(0, tk.END)
            self.time_entry.delete(0, tk.END)
        except ValueError:
            self.event_label.config(text="Nesprávny formát! Použite DD.MM.YYYY pre dátum a HH:MM pre čas")

    def update_intervals_listbox(self):
        self.intervals_listbox.delete(0, tk.END)
        for i, interval in enumerate(sorted(self.intervals, key=lambda x: x["datetime"])):
            dt = interval["datetime"].strftime("%d.%m.%Y %H:%M")
            self.intervals_listbox.insert(tk.END, f"{interval['name']} - {dt}")

    def start_countdown(self):
        if not self.intervals:
            self.event_label.config(text="Najprv pridajte aspoň jeden interval!")
            return
        # Vyber najbližší interval
        now = datetime.now()
        future_intervals = [iv for iv in self.intervals if iv["datetime"] > now]
        if not future_intervals:
            self.event_label.config(text="Žiadny interval v budúcnosti!")
            return
        future_intervals.sort(key=lambda x: x["datetime"])
        self.current_interval_index = self.intervals.index(future_intervals[0])
        self.target_datetime = future_intervals[0]["datetime"]
        self.is_counting = True
        self.open_countdown_window(future_intervals[0]["name"])

    def open_countdown_window(self, event_name):
        self.countdown_win = tk.Toplevel(self)
        self.countdown_win.title("Odpočítavanie")
        self.countdown_win.geometry("800x450")
        self.countdown_win.configure(bg=COLOR_BG)
        self.countdown_win.protocol("WM_DELETE_WINDOW", self.on_countdown_close)
        # Bind ESC na vypnutie fullscreen
        self.countdown_win.bind("<Escape>", self._exit_fullscreen_on_esc)

        # Top frame (for time)
        self.top_frame = tk.Frame(self.countdown_win, bg=COLOR_BG)
        self.top_frame.pack(expand=True, fill="both")
        # Bottom frame (for countdown)
        self.bottom_frame = tk.Frame(self.countdown_win, bg=COLOR_BG)
        self.bottom_frame.pack(expand=True, fill="both")

        # Current time label (top, big)
        self.cd_time_label = tk.Label(
            self.top_frame,
            text="--:--:--",
            font=("Helvetica", FONT_SIZE_TIME, "bold"),
            bg=COLOR_BG,
            fg=COLOR_FG,
            anchor="center",
            justify="center"
        )
        self.cd_time_label.pack(expand=True, fill="both", anchor="center")
        self.update_current_time()

        # Event name label (top, pod časom)
        self.cd_event_label = tk.Label(
            self.top_frame,
            text="Zostávajúci čas",
            font=("Helvetica", FONT_SIZE_EVENT, "bold"),
            bg=COLOR_BG,
            fg=COLOR_FG,
            anchor="center",
            justify="center"
        )
        self.cd_event_label.pack(pady=(0, 10), fill="both", anchor="center")
        Tooltip(self.cd_event_label, event_name)

        # Countdown label (bottom, even bigger)
        self.cd_countdown_label = tk.Label(
            self.bottom_frame,
            text="--:--:--",
            font=("Helvetica", FONT_SIZE_COUNTDOWN, "bold"),
            bg=COLOR_BG,
            fg=COLOR_COUNTDOWN_FG,
            anchor="center",
            justify="center"
        )
        self.cd_countdown_label.pack(expand=True, fill="both", anchor="center")

        # Fullscreen toggle button (nenápadné, vpravo dole)
        self.fullscreen = False
        self.fullscreen_btn = tk.Button(
            self.countdown_win,
            text="⛶",
            font=("Helvetica", 18),
            command=self.toggle_fullscreen,
            bg=COLOR_BTN_BG,
            fg=COLOR_BTN_FG,
            bd=0,
            activebackground=COLOR_BTN_ACTIVE_BG,
            activeforeground=COLOR_BTN_ACTIVE_FG,
            highlightthickness=0,
            cursor="hand2"
        )
        self.fullscreen_btn.place(relx=0.98, rely=0.98, anchor="se")

        # Next interval button (hidden by default)
        self.next_btn = ttk.Button(
            self.countdown_win,
            text="Pokračovať",
            command=self.start_next_interval
        )
        self.next_btn.pack(pady=10)
        self.next_btn.pack_forget()

        self.update_countdown_window()

        self._normal_geometry = None  # pre návrat z fullscreen

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            # Ulož pôvodnú veľkosť a pozíciu
            self._normal_geometry = self.countdown_win.geometry()
            # Zisti pozíciu okna
            x = self.countdown_win.winfo_rootx()
            y = self.countdown_win.winfo_rooty()
            # Nájdeme monitor, na ktorom je väčšina okna
            best_monitor = None
            max_overlap = 0
            for m in get_monitors():
                overlap_x = max(0, min(x + self.countdown_win.winfo_width(), m.x + m.width) - max(x, m.x))
                overlap_y = max(0, min(y + self.countdown_win.winfo_height(), m.y + m.height) - max(y, m.y))
                overlap = overlap_x * overlap_y
                if overlap > max_overlap:
                    max_overlap = overlap
                    best_monitor = m
            if best_monitor:
                self.countdown_win.geometry(f"{best_monitor.width}x{best_monitor.height}+{best_monitor.x}+{best_monitor.y}")
            self.countdown_win.update()
            self.countdown_win.overrideredirect(True)
            self.fullscreen_btn.config(text="⤢")
        else:
            # Vráť pôvodnú veľkosť a pozíciu
            if self._normal_geometry:
                self.countdown_win.geometry(self._normal_geometry)
            self.countdown_win.overrideredirect(False)
            self.fullscreen_btn.config(text="⛶")

    def on_countdown_close(self):
        self.is_counting = False
        self.countdown_win.destroy()
        self.destroy()

    def update_countdown_window(self):
        if not self.is_counting or not hasattr(self, 'countdown_win'):
            return
        now = datetime.now()
        if self.target_datetime <= now:
            self.cd_countdown_label.config(text="Čas vypršal!")
            self.is_counting = False
            self.next_btn.pack(pady=10)
            return
        diff = self.target_datetime - now
        total_seconds = int(diff.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        self.cd_countdown_label.config(
            text=f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        )
        self.countdown_win.after(1000, self.update_countdown_window)

    def start_next_interval(self):
        # Odstráň už uplynutý interval
        if self.current_interval_index is not None:
            del self.intervals[self.current_interval_index]
            self.update_intervals_listbox()
        # Spusti ďalší najbližší interval
        now = datetime.now()
        future_intervals = [iv for iv in self.intervals if iv["datetime"] > now]
        if not future_intervals:
            self.cd_countdown_label.config(text="Žiadny ďalší interval!")
            self.next_btn.pack_forget()
            return
        future_intervals.sort(key=lambda x: x["datetime"])
        self.current_interval_index = self.intervals.index(future_intervals[0])
        self.target_datetime = future_intervals[0]["datetime"]
        self.cd_event_label.config(text="Zostávajúci čas")
        self.is_counting = True
        self.next_btn.pack_forget()
        self.update_countdown_window()

    def update_current_time(self):
        if not hasattr(self, 'countdown_win'):
            return
        now = datetime.now().strftime("%H:%M:%S")
        self.cd_time_label.config(text=now)
        self.countdown_win.after(1000, self.update_current_time)

    def load_intervals_from_file(self):
        if not os.path.exists(FILE_NAME):
            self.event_label.config(text=f"Konfiguračný súbor {FILE_NAME} neexistuje.")
            return
        try:
            with open(FILE_NAME, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.intervals.clear()
            loaded = 0
            for item in data:
                name = item.get("name")
                dt_str = item.get("datetime")
                try:
                    dt = datetime.strptime(dt_str, "%d.%m.%Y %H:%M")
                    if dt > datetime.now():
                        self.intervals.append({"name": name, "datetime": dt})
                        loaded += 1
                except Exception as e:
                    print(f"  Chyba pri parsovaní: {e}")
                    self.event_label.config(text=f"Chyba pri načítaní: {e}")
                    continue
            self.update_intervals_listbox()
            self.event_label.config(text=f"Načítaných {loaded} intervalov zo súboru.")
        except Exception as e:
            self.event_label.config(text=f"Chyba pri načítaní: {e}")

    def _exit_fullscreen_on_esc(self, event=None):
        if self.fullscreen:
            self.toggle_fullscreen()

if __name__ == "__main__":
    app = EventCountdown()
    app.mainloop() 
