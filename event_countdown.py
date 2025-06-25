import tkinter as tk
from tkinter import ttk
from datetime import datetime
import time

class EventCountdown(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Odpočítavanie do podujatia")
        self.geometry("600x500")
        self.configure(bg="#f0f0f0")

        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12), padding=5)
        style.configure("TEntry", font=("Helvetica", 12), padding=5)
        style.configure("TButton", font=("Helvetica", 12), padding=5)

        # Event name frame
        self.name_frame = ttk.Frame(self)
        self.name_frame.pack(pady=10)
        ttk.Label(self.name_frame, text="Názov podujatia:").pack(side=tk.LEFT)
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

        # Start button
        self.start_button = ttk.Button(self, text="Spustiť odpočítavanie", command=self.start_countdown)
        self.start_button.pack(pady=10)

        self.event_label = ttk.Label(
            self,
            text="Zadajte údaje o podujatí a pridajte intervaly",
            font=("Helvetica", 14)
        )
        self.event_label.pack(pady=10)

        self.is_counting = False
        self.target_datetime = None
        self.current_interval_index = None

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
        self.countdown_win.geometry("600x300")
        self.countdown_win.configure(bg="#222")
        self.countdown_win.protocol("WM_DELETE_WINDOW", self.on_countdown_close)

        # Current time label
        self.cd_time_label = ttk.Label(
            self.countdown_win,
            text="--:--:--",
            font=("Helvetica", 18),
            background="#222",
            foreground="#fff"
        )
        self.cd_time_label.pack(pady=(20, 5))
        self.update_current_time()

        # Event name label
        self.cd_event_label = ttk.Label(
            self.countdown_win,
            text=event_name,
            font=("Helvetica", 20, "bold"),
            background="#222",
            foreground="#fff"
        )
        self.cd_event_label.pack(pady=5)

        # Countdown label
        self.cd_countdown_label = ttk.Label(
            self.countdown_win,
            text="--:--:--:--",
            font=("Helvetica", 48, "bold"),
            background="#222",
            foreground="#fff"
        )
        self.cd_countdown_label.pack(pady=20)

        # Fullscreen toggle button
        self.fullscreen = False
        self.fullscreen_btn = ttk.Button(
            self.countdown_win,
            text="Celá obrazovka",
            command=self.toggle_fullscreen
        )
        self.fullscreen_btn.pack(pady=10)

        # Next interval button (hidden by default)
        self.next_btn = ttk.Button(
            self.countdown_win,
            text="Ďalší interval",
            command=self.start_next_interval
        )
        self.next_btn.pack(pady=10)
        self.next_btn.pack_forget()

        self.update_countdown_window()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.countdown_win.attributes("-fullscreen", self.fullscreen)
        if self.fullscreen:
            self.fullscreen_btn.config(text="Ukončiť celú obrazovku")
        else:
            self.fullscreen_btn.config(text="Celá obrazovka")

    def on_countdown_close(self):
        self.is_counting = False
        self.countdown_win.destroy()

    def update_countdown_window(self):
        if not self.is_counting or not hasattr(self, 'countdown_win'):
            return
        now = datetime.now()
        if self.target_datetime <= now:
            self.cd_countdown_label.config(text="PODUJATIE SA ZAČALO!")
            self.is_counting = False
            self.next_btn.pack(pady=10)
            return
        diff = self.target_datetime - now
        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        seconds = diff.seconds % 60
        self.cd_countdown_label.config(
            text=f"{days:02d}:{hours:02d}:{minutes:02d}:{seconds:02d}"
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
        self.cd_event_label.config(text=future_intervals[0]["name"])
        self.is_counting = True
        self.next_btn.pack_forget()
        self.update_countdown_window()

    def update_current_time(self):
        if not hasattr(self, 'countdown_win'):
            return
        now = datetime.now().strftime("%H:%M:%S")
        self.cd_time_label.config(text=now)
        self.countdown_win.after(1000, self.update_current_time)

if __name__ == "__main__":
    app = EventCountdown()
    app.mainloop() 