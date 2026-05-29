"""
csv_cleaner_gui.py
Main Tkinter GUI for CSV Cleaner Tool.
Run: python csv_cleaner_gui.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os

from cleaner import clean_dataframe, build_report


# ─────────────────────────────────────────────
#  COLOUR PALETTE
# ─────────────────────────────────────────────
BG        = "#1e1e2e"
PANEL     = "#2a2a3e"
ACCENT    = "#7c6af7"
ACCENT2   = "#56cfb2"
TEXT      = "#cdd6f4"
MUTED     = "#6c7086"
WHITE     = "#ffffff"
BTN_GREEN = "#40a870"
BTN_RED   = "#e06c75"
BTN_BLUE  = "#7c6af7"
FONT_MAIN = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_H1   = ("Segoe UI", 14, "bold")
FONT_H2   = ("Segoe UI", 11, "bold")
FONT_MONO = ("Courier New", 9)


# ─────────────────────────────────────────────
#  MAIN APP CLASS
# ─────────────────────────────────────────────
class CSVCleanerApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("CSV Cleaner GUI  —  BrightNode AI")
        self.geometry("950x680")
        self.resizable(True, True)
        self.configure(bg=BG)

        self.df_original = None
        self.df_cleaned  = None
        self.filepath    = tk.StringVar(value="No file selected")

        self._build_ui()

    # ─────────────────────────────────────────
    #  UI BUILDER
    # ─────────────────────────────────────────
    def _build_ui(self):
        # ── Header ──────────────────────────
        header = tk.Frame(self, bg=ACCENT, height=54)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="  CSV Cleaner GUI",
            bg=ACCENT, fg=WHITE,
            font=FONT_H1
        ).pack(side="left", padx=16, pady=10)

        tk.Label(
            header,
            text="BrightNode AI  |  Data Cleaning Tool",
            bg=ACCENT, fg="#d0ccff",
            font=("Segoe UI", 9)
        ).pack(side="right", padx=16)

        # ── Main body: left panel + right preview ──
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=14, pady=12)

        # Left control panel
        left = tk.Frame(body, bg=PANEL, width=270)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)

        # Right preview panel
        right = tk.Frame(body, bg=PANEL)
        right.pack(side="left", fill="both", expand=True)

        self._build_left_panel(left)
        self._build_right_panel(right)

        # ── Status bar ──────────────────────
        self.status_var = tk.StringVar(value="Ready. Load a CSV file to begin.")
        status_bar = tk.Label(
            self, textvariable=self.status_var,
            bg="#13131f", fg=MUTED,
            font=("Segoe UI", 9), anchor="w", padx=12
        )
        status_bar.pack(fill="x", side="bottom", ipady=4)

    # ─────────────────────────────────────────
    #  LEFT PANEL
    # ─────────────────────────────────────────
    def _build_left_panel(self, parent):
        pad = {"padx": 16, "pady": 6}

        # Section: File
        self._section_label(parent, "FILE")

        tk.Label(parent, textvariable=self.filepath,
                 bg=PANEL, fg=MUTED, font=("Segoe UI", 8),
                 wraplength=240, justify="left").pack(anchor="w", **pad)

        self._btn(parent, "Browse CSV / Excel", self._load_file,
                  bg=BTN_BLUE).pack(fill="x", padx=16, pady=(0, 10))

        ttk.Separator(parent, orient="horizontal").pack(fill="x", padx=12, pady=4)

        # Section: Missing values
        self._section_label(parent, "FILL MISSING VALUES")

        self.fill_var = tk.StringVar(value="median")
        for label, val in [("Median", "median"), ("Mean", "mean"), ("Custom value", "custom")]:
            tk.Radiobutton(
                parent, text=label, variable=self.fill_var, value=val,
                bg=PANEL, fg=TEXT, selectcolor=ACCENT,
                activebackground=PANEL, activeforeground=WHITE,
                font=FONT_MAIN
            ).pack(anchor="w", padx=20, pady=1)

        # Custom value entry
        custom_frame = tk.Frame(parent, bg=PANEL)
        custom_frame.pack(fill="x", padx=16, pady=(4, 6))
        tk.Label(custom_frame, text="Custom:", bg=PANEL, fg=MUTED, font=FONT_MAIN).pack(side="left")
        self.custom_entry = tk.Entry(custom_frame, width=10, bg="#13131f", fg=TEXT,
                                      insertbackground=WHITE, font=FONT_MONO,
                                      relief="flat", bd=4)
        self.custom_entry.pack(side="left", padx=6)

        ttk.Separator(parent, orient="horizontal").pack(fill="x", padx=12, pady=4)

        # Section: Outliers
        self._section_label(parent, "OUTLIER HANDLING  (IQR)")

        self.outlier_var = tk.StringVar(value="cap")
        for label, val in [("Cap at IQR boundaries", "cap"),
                            ("Remove outlier rows", "remove"),
                            ("Ignore outliers", "ignore")]:
            tk.Radiobutton(
                parent, text=label, variable=self.outlier_var, value=val,
                bg=PANEL, fg=TEXT, selectcolor=ACCENT,
                activebackground=PANEL, activeforeground=WHITE,
                font=FONT_MAIN
            ).pack(anchor="w", padx=20, pady=1)

        ttk.Separator(parent, orient="horizontal").pack(fill="x", padx=12, pady=10)

        # Action buttons
        self._btn(parent, "Preview Cleaned Data", self._preview,
                  bg=ACCENT2, fg="#0a2a22").pack(fill="x", padx=16, pady=(0, 6))

        self._btn(parent, "Save As Clean CSV", self._save,
                  bg=BTN_GREEN).pack(fill="x", padx=16, pady=(0, 6))

        self._btn(parent, "Reset", self._reset,
                  bg=BTN_RED).pack(fill="x", padx=16, pady=(0, 10))

    # ─────────────────────────────────────────
    #  RIGHT PANEL
    # ─────────────────────────────────────────
    def _build_right_panel(self, parent):
        # Tab control
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=PANEL, borderwidth=0)
        style.configure("TNotebook.Tab", background="#13131f", foreground=MUTED,
                        padding=[12, 6], font=FONT_MAIN)
        style.map("TNotebook.Tab", background=[("selected", ACCENT)],
                  foreground=[("selected", WHITE)])

        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Original data
        tab_orig = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab_orig, text="  Original Data  ")
        self.tree_orig = self._build_table(tab_orig)

        # Tab 2: Cleaned data
        tab_clean = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab_clean, text="  Cleaned Data  ")
        self.tree_clean = self._build_table(tab_clean)

        # Tab 3: Report
        tab_report = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab_report, text="  Cleaning Report  ")

        self.report_text = tk.Text(
            tab_report, bg="#0d0d1a", fg=ACCENT2,
            font=FONT_MONO, relief="flat",
            padx=16, pady=14, state="disabled"
        )
        self.report_text.pack(fill="both", expand=True)

    # ─────────────────────────────────────────
    #  HELPERS
    # ─────────────────────────────────────────
    def _section_label(self, parent, text):
        tk.Label(
            parent, text=text,
            bg=PANEL, fg=ACCENT,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", padx=16, pady=(12, 2))

    def _btn(self, parent, text, command, bg=BTN_BLUE, fg=WHITE):
        return tk.Button(
            parent, text=text, command=command,
            bg=bg, fg=fg, activebackground=bg,
            activeforeground=fg, relief="flat",
            font=FONT_BOLD, cursor="hand2",
            padx=8, pady=7, bd=0
        )

    def _build_table(self, parent):
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="both", expand=True, padx=6, pady=6)

        style = ttk.Style()
        style.configure("Custom.Treeview",
                        background="#13131f",
                        foreground=TEXT,
                        fieldbackground="#13131f",
                        rowheight=24,
                        font=("Segoe UI", 9))
        style.configure("Custom.Treeview.Heading",
                        background=ACCENT,
                        foreground=WHITE,
                        font=FONT_BOLD)
        style.map("Custom.Treeview", background=[("selected", ACCENT)])

        tree = ttk.Treeview(frame, style="Custom.Treeview", show="headings")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)

        return tree

    def _load_table(self, tree, df):
        """Populate a Treeview with DataFrame data."""
        tree.delete(*tree.get_children())
        tree["columns"] = list(df.columns)

        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=110, anchor="w")

        for _, row in df.head(200).iterrows():
            tree.insert("", "end", values=list(row))

    def _set_status(self, msg):
        self.status_var.set(msg)

    # ─────────────────────────────────────────
    #  ACTIONS
    # ─────────────────────────────────────────
    def _load_file(self):
        path = filedialog.askopenfilename(
            title="Select CSV or Excel file",
            filetypes=[("CSV files", "*.csv"),
                       ("Excel files", "*.xlsx *.xls"),
                       ("All files", "*.*")]
        )
        if not path:
            return

        try:
            if path.lower().endswith(".csv"):
                self.df_original = pd.read_csv(path)
            else:
                self.df_original = pd.read_excel(path)

            self.filepath.set(os.path.basename(path))
            self._load_table(self.tree_orig, self.df_original)
            self.df_cleaned = None
            self.notebook.select(0)
            self._set_status(
                f"Loaded: {os.path.basename(path)}  |  "
                f"{len(self.df_original)} rows  x  {len(self.df_original.columns)} columns"
            )

        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def _preview(self):
        if self.df_original is None:
            messagebox.showwarning("No file", "Please load a CSV or Excel file first.")
            return

        strategy = self.fill_var.get()
        custom_val = None
        if strategy == "custom":
            try:
                custom_val = float(self.custom_entry.get())
            except ValueError:
                messagebox.showerror("Invalid value", "Please enter a valid number for custom fill value.")
                return

        outlier_method = self.outlier_var.get()

        try:
            df_copy = self.df_original.copy()
            self.df_cleaned, summary = clean_dataframe(
                df_copy,
                fill_strategy=strategy,
                custom_value=custom_val,
                outlier_method=outlier_method
            )
            self._load_table(self.tree_clean, self.df_cleaned)

            report = build_report(self.df_original, self.df_cleaned, summary)
            self.report_text.configure(state="normal")
            self.report_text.delete("1.0", "end")
            self.report_text.insert("end", report)
            self.report_text.configure(state="disabled")

            self.notebook.select(1)
            self._set_status(
                f"Preview ready  |  "
                f"Dupes removed: {summary['duplicates_removed']}  |  "
                f"Missing filled: {summary['missing_filled']}  |  "
                f"Outliers handled: {summary['outliers_handled']}"
            )

        except Exception as e:
            messagebox.showerror("Clean Error", str(e))

    def _save(self):
        if self.df_cleaned is None:
            messagebox.showwarning("Nothing to save", "Click Preview first to generate cleaned data.")
            return

        path = filedialog.asksaveasfilename(
            title="Save cleaned CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if not path:
            return

        try:
            self.df_cleaned.to_csv(path, index=False)
            self._set_status(f"Saved: {os.path.basename(path)}")
            messagebox.showinfo("Saved", f"Cleaned file saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def _reset(self):
        self.df_original = None
        self.df_cleaned  = None
        self.filepath.set("No file selected")
        self.tree_orig.delete(*self.tree_orig.get_children())
        self.tree_clean.delete(*self.tree_clean.get_children())
        self.report_text.configure(state="normal")
        self.report_text.delete("1.0", "end")
        self.report_text.configure(state="disabled")
        self.notebook.select(0)
        self._set_status("Reset. Load a CSV file to begin.")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = CSVCleanerApp()
    app.mainloop()
