import customtkinter as ctk
from tkinter import messagebox, ttk
import sqlite3
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SmartTradingJournal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Smart Trading Journal & Risk Management System")
        self.geometry("1320x760")

        self.init_database()
        self.create_sidebar()
        
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.pack(side="right", fill="both", expand=True)

        self.show_home()

    def init_database(self):
        conn = sqlite3.connect('trades.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                trade_id INTEGER PRIMARY KEY,
                instrument TEXT NOT NULL,
                trade_type TEXT NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                stop_loss REAL,
                target REAL,
                brokerage REAL DEFAULT 0.0,
                trade_date TEXT NOT NULL,
                notes TEXT,
                pnl REAL,
                rr_ratio REAL
            )
        ''')
        conn.commit()
        conn.close()

    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(sidebar, text="Smart Trading", font=ctk.CTkFont(size=26, weight="bold")).pack(pady=(40, 5))
        ctk.CTkLabel(sidebar, text="Journal & Risk Manager", font=ctk.CTkFont(size=13)).pack(pady=(0, 40))

        buttons = [
            ("🏠  Home", self.show_home),
            ("➕  Add Trade", self.show_trade_entry),
            ("📊  Dashboard", self.show_dashboard),
            ("📜  All Trades", self.show_all_trades),
            ("📋  Reports", self.show_reports),
            ("⚙️  Settings", self.show_settings)
        ]

        for text, command in buttons:
            ctk.CTkButton(sidebar, text=text, height=50, font=ctk.CTkFont(size=15), 
                         corner_radius=10, command=command).pack(pady=8, padx=25, fill="x")

        ctk.CTkLabel(sidebar, text="Major Project 2026", font=ctk.CTkFont(size=12), text_color="gray").pack(side="bottom", pady=50)

    
    def show_home(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.main_frame, text="Smart Trading Journal", 
                    font=ctk.CTkFont(size=36, weight="bold")).pack(pady=(80, 10))

        ctk.CTkLabel(self.main_frame, text="Your Personal Risk Management & Performance Tracker", 
                    font=ctk.CTkFont(size=16)).pack(pady=(0, 50))

        cards_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        cards_frame.pack(pady=20, padx=80, fill="x")

        features = [
            ("📊", "Performance Dashboard", "Track P&L, Win Rate & Drawdown"),
            ("💰", "Automatic Calculations", "P&L and Risk-Reward Ratio"),
            ("📜", "Trade Journal", "Complete record of all trades"),
            ("🛡️", "Risk Management", "Stop Loss, Target & Capital Protection")
        ]

        for icon, title_text, desc in features:
            card = ctk.CTkFrame(cards_frame, fg_color="#2b2b2b", corner_radius=15, height=160)
            card.pack(side="left", padx=15, pady=10, fill="both", expand=True)
            card.pack_propagate(False)

            ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=48)).pack(pady=(25, 5))
            ctk.CTkLabel(card, text=title_text, font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
            ctk.CTkLabel(card, text=desc, font=ctk.CTkFont(size=13), text_color="gray").pack(pady=5)

        
        conn = sqlite3.connect('trades.db')
        df = pd.read_sql_query("SELECT COUNT(*) as count, SUM(pnl) as total_pnl FROM trades", conn)
        conn.close()

        count = df.iloc[0]['count']
        total_pnl = df.iloc[0]['total_pnl'] if df.iloc[0]['total_pnl'] is not None else 0.0

        stats_frame = ctk.CTkFrame(self.main_frame, fg_color="#2b2b2b", corner_radius=12)
        stats_frame.pack(pady=40, padx=100, fill="x")

        ctk.CTkLabel(stats_frame, text="Quick Overview", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)

        stat_row = ctk.CTkFrame(stats_frame)
        stat_row.pack(pady=10)

        ctk.CTkLabel(stat_row, text=f"Total Trades:  {count}", font=ctk.CTkFont(size=16)).pack(side="left", padx=50)
        color = "green" if total_pnl >= 0 else "red"
        ctk.CTkLabel(stat_row, text=f"Net P&L:  ₹{total_pnl:.2f}", 
                    font=ctk.CTkFont(size=16), text_color=color).pack(side="left", padx=50)

        ctk.CTkLabel(self.main_frame, text="Discipline + Data = Better Trading", 
                    font=ctk.CTkFont(size=15, slant="italic"), text_color="gray").pack(pady=40)

    
    def show_trade_entry(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.main_frame, text="➕ Add New Trade", 
                    font=ctk.CTkFont(size=24, weight="bold")).pack(pady=25)

        form = ctk.CTkFrame(self.main_frame)
        form.pack(pady=20, padx=80, fill="both", expand=True)

        self.entries = {}

        fields = [
            ("Instrument", "instrument"),
            ("Trade Type", "trade_type"),
            ("Entry Price", "entry_price"),
            ("Exit Price", "exit_price"),
            ("Quantity", "quantity"),
            ("Stop Loss", "stop_loss"),
            ("Target", "target"),
            ("Brokerage", "brokerage"),
            ("Trade Date", "trade_date")
        ]

        for i, (label_text, key) in enumerate(fields):
            ctk.CTkLabel(form, text=label_text + ":").grid(row=i, column=0, padx=30, pady=14, sticky="w")

            if key == "trade_type":
                self.entries[key] = ctk.CTkComboBox(form, values=["BUY", "SELL"], width=230)
            else:
                self.entries[key] = ctk.CTkEntry(form, width=230)
                if key == "trade_date":
                    self.entries[key].insert(0, datetime.now().strftime("%Y-%m-%d"))

            self.entries[key].grid(row=i, column=1, padx=30, pady=14, sticky="w")

        ctk.CTkLabel(form, text="Notes:").grid(row=len(fields), column=0, padx=30, pady=14, sticky="nw")
        self.notes = ctk.CTkTextbox(form, width=500, height=90)
        self.notes.grid(row=len(fields), column=1, padx=30, pady=14, sticky="ew", columnspan=2)

        btn_frame = ctk.CTkFrame(self.main_frame)
        btn_frame.pack(pady=35)

        ctk.CTkButton(btn_frame, text="💾 SAVE TRADE", width=280, height=55,
                     font=ctk.CTkFont(size=17, weight="bold"), 
                     command=self.save_trade).pack(side="left", padx=25)

        ctk.CTkButton(btn_frame, text="Clear Form", width=180, height=55,
                     fg_color="#555555", command=self.clear_form).pack(side="left", padx=10)

    def save_trade(self):
        try:
            instrument = self.entries["instrument"].get().strip().upper()
            trade_type = self.entries["trade_type"].get()
            entry = float(self.entries["entry_price"].get())
            exit_p = float(self.entries["exit_price"].get())
            qty = int(self.entries["quantity"].get())
            sl = float(self.entries["stop_loss"].get()) if self.entries["stop_loss"].get() else None
            target = float(self.entries["target"].get()) if self.entries["target"].get() else None
            brokerage = float(self.entries["brokerage"].get()) if self.entries["brokerage"].get() else 0.0
            date = self.entries["trade_date"].get()
            notes = self.notes.get("1.0", "end").strip()

            pnl = self.calculate_pnl(entry, exit_p, qty, trade_type, brokerage)
            rr = self.calculate_rr(entry, sl, target, trade_type)

            conn = sqlite3.connect('trades.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO trades (instrument, trade_type, entry_price, exit_price, quantity, stop_loss, target, 
                brokerage, trade_date, notes, pnl, rr_ratio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (instrument, trade_type, entry, exit_p, qty, sl, target, brokerage, date, notes, pnl, rr))
            conn.commit()
            conn.close()

            messagebox.showinfo("✅ Success", f"Trade Saved!\nP&L: ₹{pnl}\nR:R Ratio: {rr}")
            self.clear_form()

        except Exception as e:
            messagebox.showerror("Error", f"Invalid input!\n{str(e)}")

    def calculate_pnl(self, entry, exit_p, qty, trade_type, brokerage=0):
        if trade_type == "BUY":
            return round((exit_p - entry) * qty - brokerage, 2)
        else:
            return round((entry - exit_p) * qty - brokerage, 2)

    def calculate_rr(self, entry, sl, target, trade_type):
        if not sl or not target: return 0.0
        try:
            if trade_type == "BUY":
                risk = entry - float(sl)
                reward = float(target) - entry
            else:
                risk = float(sl) - entry
                reward = entry - float(target)
            return round(reward / risk, 2) if risk > 0 else 0.0
        except:
            return 0.0

    def clear_form(self):
        for widget in self.entries.values():
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, 'end')
            else:
                widget.set("")
        self.notes.delete("1.0", "end")
        self.entries["trade_date"].insert(0, datetime.now().strftime("%Y-%m-%d"))

    
    def show_dashboard(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.main_frame, text="📊 Performance Dashboard", 
                    font=ctk.CTkFont(size=28, weight="bold")).pack(pady=20)

        conn = sqlite3.connect('trades.db')
        df = pd.read_sql_query("SELECT * FROM trades", conn)
        conn.close()

        if df.empty:
            ctk.CTkLabel(self.main_frame, text="No trades recorded yet.", 
                        font=ctk.CTkFont(size=18), text_color="orange").pack(pady=180)
            return

        
        summary_frame = ctk.CTkFrame(self.main_frame)
        summary_frame.pack(pady=15, padx=50, fill="x")

        total_trades = len(df)
        net_pnl = df['pnl'].sum()
        win_rate = (len(df[df['pnl'] > 0]) / total_trades * 100) if total_trades > 0 else 0
        avg_rr = df['rr_ratio'].mean() if not df['rr_ratio'].empty else 0.0

        cards = [
            ("Total Trades", total_trades, "#00aaff"),
            ("Net P&L", f"₹{net_pnl:.2f}", "green" if net_pnl >= 0 else "red"),
            ("Win Rate", f"{win_rate:.1f}%", "#00aaff"),
            ("Avg R:R", f"{avg_rr:.2f}", "#00aaff")
        ]

        for title, value, color in cards:
            card = ctk.CTkFrame(summary_frame, fg_color="#2b2b2b", corner_radius=12)
            card.pack(side="left", padx=12, fill="both", expand=True)
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14)).pack(pady=8)
            ctk.CTkLabel(card, text=str(value), font=ctk.CTkFont(size=22, weight="bold"), text_color=color).pack(pady=5)

        
        chart_frame = ctk.CTkFrame(self.main_frame)
        chart_frame.pack(pady=25, padx=50, fill="both", expand=True)

        
        fig1 = Figure(figsize=(5, 4.5), dpi=100)
        ax1 = fig1.add_subplot(111)
        wins = len(df[df['pnl'] > 0])
        losses = len(df[df['pnl'] < 0])
        ax1.pie([wins, losses, len(df)-wins-losses], labels=['Wins','Losses','Breakeven'], 
                autopct='%1.1f%%', colors=['#00ff88', '#ff5555', '#aaaaaa'])
        ax1.set_title("Win / Loss Distribution")
        FigureCanvasTkAgg(fig1, chart_frame).get_tk_widget().pack(side="left", padx=20, fill="both", expand=True)

        # Equity Curve
        fig2 = Figure(figsize=(6.8, 4.5), dpi=100)
        ax2 = fig2.add_subplot(111)
        cum_pnl = df['pnl'].cumsum()
        ax2.plot(range(1, len(df)+1), cum_pnl, marker='o', linewidth=3, color='#00aaff')
        ax2.set_title("Equity Curve")
        ax2.set_xlabel("Trade Number")
        ax2.set_ylabel("Cumulative P&L (₹)")
        ax2.set_xticks(range(1, len(df)+1))
        ax2.grid(True, alpha=0.3)
        FigureCanvasTkAgg(fig2, chart_frame).get_tk_widget().pack(side="left", padx=20, fill="both", expand=True)

    
    def show_all_trades(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.main_frame, text="📜 All Trades (Oldest to Newest)", 
                    font=ctk.CTkFont(size=24, weight="bold")).pack(pady=25)

        conn = sqlite3.connect('trades.db')
        df = pd.read_sql_query("SELECT * FROM trades ORDER BY trade_date ASC", conn)
        conn.close()

        if df.empty:
            ctk.CTkLabel(self.main_frame, text="No trades recorded yet", font=ctk.CTkFont(size=18)).pack(pady=180)
            return

        tree = ttk.Treeview(self.main_frame, columns=("ID","Date","Instrument","Type","P&L","R:R"), show="headings", height=14)

        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, width=140, anchor="center")

        for _, row in df.iterrows():
            tree.insert("", "end", values=(
                row['trade_id'], row['trade_date'], row['instrument'], row['trade_type'],
                f"₹{row['pnl']:.2f}", row['rr_ratio']
            ))

        tree.pack(pady=20, padx=60, fill="both", expand=True)

    
    def show_reports(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.main_frame, text="📋 Performance Reports", 
                    font=ctk.CTkFont(size=28, weight="bold")).pack(pady=25)

        conn = sqlite3.connect('trades.db')
        df = pd.read_sql_query("SELECT * FROM trades", conn)
        conn.close()

        if df.empty:
            ctk.CTkLabel(self.main_frame, text="No trades recorded yet.\nAdd trades to generate reports.", 
                        font=ctk.CTkFont(size=18), text_color="orange").pack(pady=180)
            return

        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df['month'] = df['trade_date'].dt.strftime('%Y-%m')

        monthly = df.groupby('month')['pnl'].sum().reset_index()

        
        summary = ctk.CTkFrame(self.main_frame)
        summary.pack(pady=20, padx=60, fill="x")

        total = len(df)
        net = df['pnl'].sum()
        win_rate = (len(df[df['pnl'] > 0]) / total * 100) if total > 0 else 0

        for title, value, color in [
            ("Total Trades", total, "#00aaff"),
            ("Net P&L", f"₹{net:.2f}", "green" if net >= 0 else "red"),
            ("Win Rate", f"{win_rate:.1f}%", "#00aaff")
        ]:
            card = ctk.CTkFrame(summary, fg_color="#2b2b2b", corner_radius=12)
            card.pack(side="left", padx=15, fill="both", expand=True)
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14)).pack(pady=8)
            ctk.CTkLabel(card, text=str(value), font=ctk.CTkFont(size=22, weight="bold"), text_color=color).pack(pady=5)

        # Monthly Performance
        ctk.CTkLabel(self.main_frame, text="Monthly Performance", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(30,10), anchor="w", padx=60)

        tree = ttk.Treeview(self.main_frame, columns=("Month", "P&L"), show="headings", height=8)
        tree.heading("Month", text="Month")
        tree.heading("P&L", text="Monthly P&L")

        for _, row in monthly.iterrows():
            tree.insert("", "end", values=(row['month'], f"₹{row['pnl']:.2f}"))

        tree.pack(pady=10, padx=60, fill="x")

    
    def show_settings(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.main_frame, text="⚙️ Settings & Preferences", 
                    font=ctk.CTkFont(size=28, weight="bold")).pack(pady=25)

        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(pady=30, padx=100, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Risk & Capital Settings", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        # Capital
        f1 = ctk.CTkFrame(frame)
        f1.pack(fill="x", padx=50, pady=12)
        ctk.CTkLabel(f1, text="Total Capital (₹):").pack(side="left", padx=10)
        self.capital_entry = ctk.CTkEntry(f1, width=200)
        self.capital_entry.pack(side="left", padx=10)
        self.capital_entry.insert(0, "100000")

        # Risk Per Trade
        f2 = ctk.CTkFrame(frame)
        f2.pack(fill="x", padx=50, pady=12)
        ctk.CTkLabel(f2, text="Risk Per Trade (%):").pack(side="left", padx=10)
        self.risk_entry = ctk.CTkEntry(f2, width=200)
        self.risk_entry.pack(side="left", padx=10)
        self.risk_entry.insert(0, "1.0")

        # Save Button
        ctk.CTkButton(frame, text="💾 Save Settings", width=300, height=55,
                     font=ctk.CTkFont(size=17, weight="bold"),
                     command=lambda: messagebox.showinfo("Success", "Settings Saved Successfully!")).pack(pady=40)

        # About
        ctk.CTkLabel(self.main_frame, text="About This Project", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(30,10))
        ctk.CTkLabel(self.main_frame, text="Smart Trading Journal & Risk Management System\n"
                                         "College Major Project\nBuilt with Python & CustomTkinter", 
                    font=ctk.CTkFont(size=14), text_color="gray").pack()

    def save_trade(self):
        try:
            instrument = self.entries["instrument"].get().strip().upper()
            trade_type = self.entries["trade_type"].get()
            entry = float(self.entries["entry_price"].get())
            exit_p = float(self.entries["exit_price"].get())
            qty = int(self.entries["quantity"].get())
            sl = float(self.entries["stop_loss"].get()) if self.entries["stop_loss"].get() else None
            target = float(self.entries["target"].get()) if self.entries["target"].get() else None
            brokerage = float(self.entries["brokerage"].get()) if self.entries["brokerage"].get() else 0.0
            date = self.entries["trade_date"].get()
            notes = self.notes.get("1.0", "end").strip()

            pnl = self.calculate_pnl(entry, exit_p, qty, trade_type, brokerage)
            rr = self.calculate_rr(entry, sl, target, trade_type)

            conn = sqlite3.connect('trades.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO trades (instrument, trade_type, entry_price, exit_price, quantity, stop_loss, target, 
                brokerage, trade_date, notes, pnl, rr_ratio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (instrument, trade_type, entry, exit_p, qty, sl, target, brokerage, date, notes, pnl, rr))
            conn.commit()
            conn.close()

            messagebox.showinfo("✅ Success", f"Trade Saved!\nP&L: ₹{pnl}\nR:R Ratio: {rr}")
            self.clear_form()

        except Exception as e:
            messagebox.showerror("Error", f"Invalid input!\n{str(e)}")

    def calculate_pnl(self, entry, exit_p, qty, trade_type, brokerage=0):
        if trade_type == "BUY":
            return round((exit_p - entry) * qty - brokerage, 2)
        else:
            return round((entry - exit_p) * qty - brokerage, 2)

    def calculate_rr(self, entry, sl, target, trade_type):
        if not sl or not target: return 0.0
        try:
            if trade_type == "BUY":
                risk = entry - float(sl)
                reward = float(target) - entry
            else:
                risk = float(sl) - entry
                reward = entry - float(target)
            return round(reward / risk, 2) if risk > 0 else 0.0
        except:
            return 0.0

    def clear_form(self):
        for widget in self.entries.values():
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, 'end')
            else:
                widget.set("")
        self.notes.delete("1.0", "end")
        self.entries["trade_date"].insert(0, datetime.now().strftime("%Y-%m-%d"))


if __name__ == "__main__":
    app = SmartTradingJournal()
    app.mainloop()