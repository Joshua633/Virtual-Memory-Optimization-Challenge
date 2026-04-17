"""
Evaluator Tab: Compare LRU vs Optimal on a reference string.
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from paging import PagingSimulator

class EvaluatorTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        frame = ttk.LabelFrame(self, text="Parameters", padding=5)
        frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(frame, text="Number of page frames:").grid(row=0, column=0, sticky='w')
        self.frames_entry = ttk.Entry(frame, width=10)
        self.frames_entry.grid(row=0, column=1, padx=5)
        self.frames_entry.insert(0, "3")

        ttk.Label(frame, text="Reference string (space-separated):").grid(row=1, column=0, sticky='w')
        self.ref_entry = ttk.Entry(frame, width=50)
        self.ref_entry.grid(row=1, column=1, columnspan=2, padx=5)
        self.ref_entry.insert(0, "1 2 3 4 1 2 5 1 2 3 4 5")

        eval_btn = ttk.Button(frame, text="Compare Algorithms", command=self.evaluate)
        eval_btn.grid(row=2, column=1, pady=10)

        self.result_text = scrolledtext.ScrolledText(self, height=20, font=("Courier", 10))
        self.result_text.pack(fill='both', expand=True, padx=5, pady=5)

    def evaluate(self):
        try:
            num_frames = int(self.frames_entry.get().strip())
            if num_frames <= 0:
                raise ValueError
            ref_str = self.ref_entry.get().strip()
            references = [int(x) for x in ref_str.split()]
            if not references:
                raise ValueError
        except:
            messagebox.showerror("Error", "Invalid input.")
            return

        # LRU
        sim_lru = PagingSimulator(num_frames)
        faults_lru = 0
        for page in references:
            if sim_lru.access_page(page, algorithm='LRU'):
                faults_lru += 1

        # Optimal
        sim_opt = PagingSimulator(num_frames)
        faults_opt = 0
        for idx, page in enumerate(references):
            if sim_opt.access_page(page, future_refs=references, current_index=idx, algorithm='OPTIMAL'):
                faults_opt += 1

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "==== Page Replacement Evaluation ====\n\n")
        self.result_text.insert(tk.END, f"Number of frames: {num_frames}\n")
        self.result_text.insert(tk.END, f"Reference string: {references}\n\n")
        self.result_text.insert(tk.END, f"LRU page faults     : {faults_lru}\n")
        self.result_text.insert(tk.END, f"Optimal page faults : {faults_opt}\n\n")
        if faults_opt < faults_lru:
            self.result_text.insert(tk.END, "Optimal performs better (fewer faults).\n")
        elif faults_opt > faults_lru:
            self.result_text.insert(tk.END, "LRU performs better (unusual, but possible).\n")
        else:
            self.result_text.insert(tk.END, "Both algorithms have the same number of faults.\n")
