import tkinter as tk
from tkinter import ttk
from datetime import datetime
import time

class EventCountdown(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Odpočítavanie do podujatia")
        self.geometry("600x400")
        self.configure(bg="#f0f0f0")

        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12), padding=5)
        style.configure("TEntry", font=("Helvetica", 12), padding=5)
        style.configure("TButton", font=("Helvetica", 12), padding=5)

        # Event name frame
        self.name_frame = ttk.Frame(self)
        self.name_frame.pack(pady=20)
        
        ttk.Label(self.name_frame, text="Názov podujatia:").pack(side=tk.LEFT)
        self.event_name = ttk.Entry(self.name_frame, width=30)
        self.event_name.pack(side=tk.LEFT, padx=5)

        # DateTime frame
        self.datetime_frame = ttk.Frame(self)
        self.datetime_frame.pack(pady=20)

        ttk.Label(self.datetime_frame, text="Dátum (DD.MM.YYYY):").pack(side=tk.LEFT)
        self.date_entry = ttk.Entry(self.datetime_frame, width=15)
        self.date_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(self.datetime_frame, text="Čas (HH:MM):").pack(side=tk.LEFT)
        self.time_entry = ttk.Entry(self.datetime_frame, width=10)
        self.time_entry.pack(side=tk.LEFT, padx=5)

        # Start button
        self.start_button = ttk.Button(self, text="Spustiť odpočítavanie", command=self.start_countdown)
        self.start_button.pack(pady=20)

        # Countdown display
        self.countdown_frame = ttk.Frame(self)
        self.countdown_frame.pack(pady=20)

        self.countdown_label = ttk.Label(
            self.countdown_frame,
            text="--:--:--:--",
            font=("Helvetica", 36, "bold")
        )
        self.countdown_label.pack()

        self.event_label = ttk.Label(
            self,
            text="Zadajte údaje o podujatí",
            font=("Helvetica", 14)
        )
        self.event_label.pack(pady=20)

        self.is_counting = False
        self.target_datetime = None

    def start_countdown(self):
        try:
            date_str = self.date_entry.get()
            time_str = self.time_entry.get()
            event_name = self.event_name.get()

            if not all([date_str, time_str, event_name]):
                self.event_label.config(text="Prosím vyplňte všetky údaje!")
                return

            # Parse date and time
            self.target_datetime = datetime.strptime(
                f"{date_str} {time_str}",
                "%d.%m.%Y %H:%M"
            )

            if self.target_datetime <= datetime.now():
                self.event_label.config(text="Zadajte budúci dátum a čas!")
                return

            self.event_label.config(text=f"Odpočítavanie do: {event_name}")
            self.is_counting = True
            self.open_countdown_window(event_name)

        except ValueError:
            self.event_label.config(
                text="Nesprávny formát! Použite DD.MM.YYYY pre dátum a HH:MM pre čas"
            )

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

    def update_current_time(self):
        if not hasattr(self, 'countdown_win') or not self.is_counting:
            return
        now = datetime.now().strftime("%H:%M:%S")
        self.cd_time_label.config(text=now)
        self.countdown_win.after(1000, self.update_current_time)

if __name__ == "__main__":
    app = EventCountdown()
    app.mainloop() 