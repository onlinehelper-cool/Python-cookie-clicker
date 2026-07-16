import tkinter as tk
from tkinter import messagebox
import json
import time
import os

SAVE_FILE = "cookie_save.json"
AUTOSAVE_INTERVAL = 5000  # ms
PRICE_MULTIPLIER = 1.15


class CookieClicker:
    def __init__(self, root):
        self.root = root
        root.title("Cookie Clicker")
        root.configure(bg="#2a1f1a")

        root.attributes("-fullscreen", True)
        root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))
        root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.cookies = 0.0
        self.last_tick = time.perf_counter()

        
        self.upgrades = [
            {"name": "Cursor", "owned": 0, "power": 0.1, "cost": 15},
            {"name": "Grandma", "owned": 0, "power": 1, "cost": 100},
            {"name": "Farm", "owned": 0, "power": 8, "cost": 1100},
            {"name": "Mine", "owned": 0, "power": 47, "cost": 12000},
            {"name": "Factory", "owned": 0, "power": 260, "cost": 130000},
            {"name": "Bank", "owned": 0, "power": 1400, "cost": 1400000},
            {"name": "Temple", "owned": 0, "power": 7800, "cost": 20000000},
            {"name": "Wizard Tower", "owned": 0, "power": 44000, "cost": 330000000},
            {"name": "Shipment", "owned": 0, "power": 260000, "cost": 5100000000},
            {"name": "Alchemy Lab", "owned": 0, "power": 1600000, "cost": 75000000000},
            {"name": "Portal", "owned": 0, "power": 10000000, "cost": 1000000000000},
            {"name": "Time Machine", "owned": 0, "power": 65000000, "cost": 14000000000000},
            {"name": "Antimatter Condenser", "owned": 0, "power": 430000000, "cost": 170000000000000},
            {"name": "Prism", "owned": 0, "power": 2900000000, "cost": 2100000000000000},
            {"name": "Chancemaker", "owned": 0, "power": 21000000000, "cost": 26000000000000000},
            {"name": "Fractal Engine", "owned": 0, "power": 150000000000, "cost": 310000000000000000},
            {"name": "Javascript Console", "owned": 0, "power": 1100000000000, "cost": 71000000000000000000},
            {"name": "Idleverse", "owned": 0, "power": 8300000000000, "cost": 12000000000000000000000},
            {"name": "Cortex Baker", "owned": 0, "power": 64000000000000, "cost": 1900000000000000000000000},
        ]

        self.main = tk.Frame(root, bg="#2a1f1a")
        self.main.pack(side="left", fill="both", expand=True)

        self.shop = tk.Frame(root, bg="#1a120d", width=520)
        self.shop.pack(side="right", fill="y")
        self.shop.pack_propagate(False)

        tk.Label(
            self.main,
            text="🍪 COOKIE CLICKER 🍪",
            font=("Arial", 36, "bold"),
            fg="#fbbf24",
            bg="#2a1f1a"
        ).pack(pady=20)

        tk.Button(
            self.main,
            text="🍪",
            font=("Arial", 100),
            bg="#fbbf24",
            fg="#2a1f1a",
            activebackground="#fde68a",
            command=self.click_cookie
        ).pack(pady=40)

        self.cookie_label = tk.Label(self.main, font=("Arial", 18), fg="#f8fafc", bg="#2a1f1a")
        self.cookie_label.pack()

        self.cps_label = tk.Label(self.main, font=("Arial", 18), fg="#f8fafc", bg="#2a1f1a")
        self.cps_label.pack(pady=10)

        canvas = tk.Canvas(self.shop, bg="#1a120d", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.shop, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.scroll = tk.Frame(canvas, bg="#1a120d")
        canvas.create_window((260, 0), window=self.scroll, anchor="n")

        self.scroll.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        self.buttons = []
        for i in range(len(self.upgrades)):
            btn = tk.Button(
                self.scroll,
                width=42,
                wraplength=460,
                font=("Arial", 11, "bold"),
                bg="#6b4f3f",
                fg="#fde68a",
                state=tk.DISABLED,
                command=lambda i=i: self.buy(i)
            )
            btn.pack(pady=6)
            self.buttons.append(btn)

        self.load_game()
        self.update_ui()
        self.tick()
        self.auto_save()

    def format(self, num):
        units = [
            (1e30, "Nonillion"),
            (1e27, "Octillion"),
            (1e24, "Septillion"),
            (1e21, "Sextillion"),
            (1e18, "Quintillion"),
            (1e15, "Quadrillion"),
            (1e12, "Trillion"),
            (1e9, "Billion"),
            (1e6, "Million"),
            (1e3, "Thousand"),
        ]

        for value, name in units:
            if num >= value:
                return f"{num / value:.2f} {name}"

        return f"{num:.2f}"

    def get_cps(self):
        return sum(u["owned"] * u["power"] for u in self.upgrades)

    def click_cookie(self):
        self.cookies += 1

    def buy(self, i):
        u = self.upgrades[i]
        if self.cookies >= u["cost"]:
            self.cookies -= u["cost"]
            u["owned"] += 1
            u["cost"] = int(u["cost"] * PRICE_MULTIPLIER)

    def tick(self):
        now = time.perf_counter()
        delta = now - self.last_tick
        self.last_tick = now
        self.cookies += self.get_cps() * delta
        self.update_ui()
        self.root.after(16, self.tick)

    def update_ui(self):
        self.cookie_label.config(text=f"Cookies: {self.format(self.cookies)} 🍪")
        self.cps_label.config(text=f"Cookies / Second: {self.format(self.get_cps())}")

        for btn, u in zip(self.buttons, self.upgrades):
            affordable = self.cookies >= u["cost"]
            btn.config(
                text=f"{u['name']} (Owned: {u['owned']})\n"
                     f"+{self.format(u['power'])} / sec\n"
                     f"Cost: {self.format(u['cost'])}",
                state=tk.NORMAL if affordable else tk.DISABLED,
                bg="#fbbf24" if affordable else "#6b4f3f",
                fg="#2a1f1a" if affordable else "#fde68a"
            )

    def save_game(self):
        with open(SAVE_FILE, "w") as f:
            json.dump({"cookies": self.cookies, "upgrades": self.upgrades}, f)

    def load_game(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
                self.cookies = data.get("cookies", 0)
                self.upgrades = data.get("upgrades", self.upgrades)

    def auto_save(self):
        self.save_game()
        self.root.after(AUTOSAVE_INTERVAL, self.auto_save)

    def on_close(self):
        self.save_game()
        self.root.destroy()


def main():
    root = tk.Tk()
    CookieClicker(root)
    root.mainloop()


if __name__ == "__main__":
    main()
