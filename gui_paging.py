"""
Paging Simulation Tab: step-by-step paging with LRU/Optimal.
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from paging import PagingSimulator

class PagingTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.sim = None
        self.references = []
        self.steps = []   # list of (fault, frames_copy, page_table_copy, lru_queue_copy)
        self.step_idx = -1
        self.fault_count = 0

        self.setup_ui()

    def setup_ui(self):
        # Parameters frame
        param_frame = ttk.LabelFrame(self, text="Parameters", padding=5)
        param_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(param_frame, text="Number of page frames:").grid(row=0, column=0, sticky='w')
        self.frames_entry = ttk.Entry(param_frame, width=10)
        self.frames_entry.grid(row=0, column=1, padx=5)
        self.frames_entry.insert(0, "3")

        ttk.Label(param_frame, text="Reference string (space-separated):").grid(row=1, column=0, sticky='w')
        self.ref_entry = ttk.Entry(param_frame, width=50)
        self.ref_entry.grid(row=1, column=1, columnspan=2, padx=5)
        self.ref_entry.insert(0, "1 2 3 4 1 2 5 1 2 3 4 5")

        ttk.Label(param_frame, text="Algorithm:").grid(row=2, column=0, sticky='w')
        self.algo_combo = ttk.Combobox(param_frame, values=["LRU", "OPTIMAL"], state="readonly")
        self.algo_combo.grid(row=2, column=1, sticky='w')
        self.algo_combo.current(0)

        run_btn = ttk.Button(param_frame, text="Run Simulation", command=self.run_simulation)
        run_btn.grid(row=2, column=2, padx=10)

        # Step control buttons
        control_frame = ttk.Frame(self)
        control_frame.pack(fill='x', padx=5, pady=5)
        self.prev_btn = ttk.Button(control_frame, text="<< Previous", command=self.prev_step, state='disabled')
        self.prev_btn.pack(side='left', padx=5)
        self.next_btn = ttk.Button(control_frame, text="Next Step >>", command=self.next_step, state='disabled')
        self.next_btn.pack(side='left', padx=5)
        self.reset_btn = ttk.Button(control_frame, text="Reset Simulation", command=self.reset, state='disabled')
        self.reset_btn.pack(side='left', padx=5)

        # Display area
        display_frame = ttk.LabelFrame(self, text="Simulation State", padding=5)
        display_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self.text_area = scrolledtext.ScrolledText(display_frame, height=20, width=80, font=("Courier", 10))
        self.text_area.pack(fill='both', expand=True)

    def run_simulation(self):
        try:
            num_frames = int(self.frames_entry.get().strip())
            if num_frames <= 0:
                raise ValueError
            ref_str = self.ref_entry.get().strip()
            self.references = [int(x) for x in ref_str.split()]
            if not self.references:
                raise ValueError
        except:
            messagebox.showerror("Error", "Invalid input. Use positive integer for frames and space-separated page numbers.")
            return

        algo = self.algo_combo.get()
        sim = PagingSimulator(num_frames)
        self.steps = []
        self.fault_count = 0

        # Simulate all steps
        for idx, page in enumerate(self.references):
            if algo == "OPTIMAL":
                fault = sim.access_page(page, future_refs=self.references, current_index=idx, algorithm="OPTIMAL")
            else:
                fault = sim.access_page(page, algorithm="LRU")
            if fault:
                self.fault_count += 1
            self.steps.append((fault, sim.frames.copy(), sim.page_table.copy(), sim.lru_queue.copy()))

        self.step_idx = -1
        self.next_btn.config(state='normal')
        self.prev_btn.config(state='disabled')
        self.reset_btn.config(state='normal')
        self.next_step()

    def next_step(self):
        if self.step_idx + 1 >= len(self.steps):
            if self.steps:
                messagebox.showinfo("End", f"Simulation complete.\nTotal page faults: {self.fault_count}")
            self.next_btn.config(state='disabled')
            return
        self.step_idx += 1
        self.update_display()
        self.prev_btn.config(state='normal')
        if self.step_idx == len(self.steps) - 1:
            self.next_btn.config(state='disabled')

    def prev_step(self):
        if self.step_idx - 1 < 0:
            self.prev_btn.config(state='disabled')
            return
        self.step_idx -= 1
        self.update_display()
        self.next_btn.config(state='normal')
        if self.step_idx == 0:
            self.prev_btn.config(state='disabled')

    def update_display(self):
        fault, frames, pt, lru = self.steps[self.step_idx]
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, f"Step {self.step_idx+1} of {len(self.steps)}\n")
        self.text_area.insert(tk.END, f"Accessing page: {self.references[self.step_idx]}\n")
        self.text_area.insert(tk.END, f"Page fault: {'YES' if fault else 'NO'}\n\n")
        self.text_area.insert(tk.END, "Current page frames:\n")
        self.text_area.insert(tk.END, "Frame | Page\n------+-----\n")
        for i, p in enumerate(frames):
            self.text_area.insert(tk.END, f"  {i:2}  |  {p if p is not None else '-'}\n")
        self.text_area.insert(tk.END, f"\nPage table: {pt}\n")
        self.text_area.insert(tk.END, f"LRU order (most recent last): {lru}\n")

    def reset(self):
        self.step_idx = -1
        self.steps = []
        self.text_area.delete(1.0, tk.END)
        self.next_btn.config(state='disabled')
        self.prev_btn.config(state='disabled')
        self.reset_btn.config(state='disabled')
