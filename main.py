import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
from collections import OrderedDict
import random

# -------------------------------
# Paging Simulator (same logic as before)
# -------------------------------
class PagingSimulator:
    def __init__(self, num_frames: int):
        self.num_frames = num_frames
        self.frames = [None] * num_frames
        self.page_table = {}
        self.lru_queue = []

    def _update_lru(self, page: int):
        if page in self.lru_queue:
            self.lru_queue.remove(page)
        self.lru_queue.append(page)

    def _get_optimal_victim(self, future_refs: list, current_index: int) -> int:
        page_to_frame = {page: idx for idx, page in enumerate(self.frames) if page is not None}
        for page, frame in page_to_frame.items():
            if page not in future_refs[current_index+1:]:
                return frame
        farthest = -1
        victim_frame = 0
        for page, frame in page_to_frame.items():
            next_use = future_refs[current_index+1:].index(page)
            if next_use > farthest:
                farthest = next_use
                victim_frame = frame
        return victim_frame

    def access_page(self, page: int, future_refs: list = None, current_index: int = -1, algorithm: str = 'LRU') -> bool:
        if page in self.page_table:
            self._update_lru(page)
            return False
        # Page fault
        free_frame = None
        for i, p in enumerate(self.frames):
            if p is None:
                free_frame = i
                break
        if free_frame is not None:
            self.frames[free_frame] = page
            self.page_table[page] = free_frame
            self._update_lru(page)
            return True
        # Replacement needed
        if algorithm == 'LRU':
            victim_page = self.lru_queue.pop(0)
            victim_frame = self.page_table[victim_page]
            del self.page_table[victim_page]
            self.frames[victim_frame] = page
            self.page_table[page] = victim_frame
            self._update_lru(page)
            return True
        elif algorithm == 'OPTIMAL':
            victim_frame = self._get_optimal_victim(future_refs, current_index)
            victim_page = self.frames[victim_frame]
            del self.page_table[victim_page]
            self.frames[victim_frame] = page
            self.page_table[page] = victim_frame
            self._update_lru(page)
            return True
        return False

    def reset(self):
        self.frames = [None] * self.num_frames
        self.page_table = {}
        self.lru_queue = []

# -------------------------------
# Segmentation Simulator (same logic, but returns info for GUI)
# -------------------------------
class SegmentationSimulator:
    def __init__(self, memory_size: int, strategy: str = 'first-fit'):
        self.memory_size = memory_size
        self.strategy = strategy.lower()
        self.free_list = [(0, memory_size)]
        self.allocated = {}

    def _merge_free_blocks(self):
        self.free_list.sort(key=lambda x: x[0])
        new_free = []
        for start, size in self.free_list:
            if new_free and new_free[-1][0] + new_free[-1][1] == start:
                prev_start, prev_size = new_free.pop()
                new_free.append((prev_start, prev_size + size))
            else:
                new_free.append((start, size))
        self.free_list = new_free

    def allocate(self, name: str, size: int) -> (bool, str):
        if size <= 0:
            return False, "Size must be positive."
        if name in self.allocated:
            return False, f"Segment '{name}' already exists."
        best_idx = -1
        if self.strategy == 'first-fit':
            for i, (start, free_sz) in enumerate(self.free_list):
                if free_sz >= size:
                    best_idx = i
                    break
        elif self.strategy == 'best-fit':
            best_fit = None
            best_fit_size = sys.maxsize
            for i, (start, free_sz) in enumerate(self.free_list):
                if free_sz >= size and free_sz < best_fit_size:
                    best_fit_size = free_sz
                    best_fit = i
            best_idx = best_fit
        else:
            return False, "Unknown strategy."
        if best_idx == -1:
            return False, f"Not enough contiguous memory for {size} bytes."
        start, free_sz = self.free_list.pop(best_idx)
        self.allocated[name] = (start, size)
        if free_sz > size:
            self.free_list.append((start + size, free_sz - size))
        self._merge_free_blocks()
        return True, f"Segment '{name}' allocated."

    def deallocate(self, name: str) -> (bool, str):
        if name not in self.allocated:
            return False, f"Segment '{name}' not found."
        start, size = self.allocated.pop(name)
        self.free_list.append((start, size))
        self._merge_free_blocks()
        return True, f"Segment '{name}' deallocated."

    def get_memory_blocks(self):
        """Return list of (start, size, type, name) for drawing."""
        blocks = []
        for name, (start, size) in self.allocated.items():
            blocks.append((start, size, "allocated", name))
        for start, size in self.free_list:
            blocks.append((start, size, "free", ""))
        blocks.sort(key=lambda x: x[0])
        return blocks

    def fragmentation_metric(self):
        total_free = sum(sz for _, sz in self.free_list)
        largest_free = max((sz for _, sz in self.free_list), default=0)
        if total_free == 0:
            return 0.0
        return 1 - (largest_free / total_free)

# -------------------------------
# GUI Application
# -------------------------------
class VirtualMemoryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Memory Management Tool")
        self.root.geometry("900x700")
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Tabs
        self.paging_tab = ttk.Frame(self.notebook)
        self.seg_tab = ttk.Frame(self.notebook)
        self.eval_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.paging_tab, text="Paging Simulation")
        self.notebook.add(self.seg_tab, text="Segmentation")
        self.notebook.add(self.eval_tab, text="Page Replacement Evaluator")

        self.setup_paging_tab()
        self.setup_segmentation_tab()
        self.setup_evaluator_tab()

    # -------------------------------
    # Paging Tab
    # -------------------------------
    def setup_paging_tab(self):
        frame_top = ttk.LabelFrame(self.paging_tab, text="Parameters", padding=5)
        frame_top.pack(fill='x', padx=5, pady=5)

        ttk.Label(frame_top, text="Number of page frames:").grid(row=0, column=0, sticky='w')
        self.p_frames_entry = ttk.Entry(frame_top, width=10)
        self.p_frames_entry.grid(row=0, column=1, padx=5)
        self.p_frames_entry.insert(0, "3")

        ttk.Label(frame_top, text="Reference string (space-separated):").grid(row=1, column=0, sticky='w')
        self.p_ref_entry = ttk.Entry(frame_top, width=50)
        self.p_ref_entry.grid(row=1, column=1, columnspan=2, padx=5)
        self.p_ref_entry.insert(0, "1 2 3 4 1 2 5 1 2 3 4 5")

        ttk.Label(frame_top, text="Algorithm:").grid(row=2, column=0, sticky='w')
        self.p_algo = ttk.Combobox(frame_top, values=["LRU", "OPTIMAL"], state="readonly")
        self.p_algo.grid(row=2, column=1, sticky='w')
        self.p_algo.current(0)

        btn_run = ttk.Button(frame_top, text="Run Simulation", command=self.run_paging_simulation)
        btn_run.grid(row=2, column=2, padx=10)

        # Step control
        self.p_step_idx = 0
        self.p_references = []
        self.p_sim = None
        self.p_steps = []  # list of (fault_occurred, frames_copy)
        self.p_fault_count = 0

        frame_control = ttk.Frame(self.paging_tab)
        frame_control.pack(fill='x', padx=5, pady=5)
        self.p_btn_prev = ttk.Button(frame_control, text="<< Previous", command=self.paging_prev_step, state='disabled')
        self.p_btn_prev.pack(side='left', padx=5)
        self.p_btn_next = ttk.Button(frame_control, text="Next Step >>", command=self.paging_next_step, state='disabled')
        self.p_btn_next.pack(side='left', padx=5)
        self.p_btn_reset = ttk.Button(frame_control, text="Reset Simulation", command=self.paging_reset, state='disabled')
        self.p_btn_reset.pack(side='left', padx=5)

        # Display area
        frame_display = ttk.LabelFrame(self.paging_tab, text="Simulation State", padding=5)
        frame_display.pack(fill='both', expand=True, padx=5, pady=5)

        self.p_text = scrolledtext.ScrolledText(frame_display, height=20, width=80, font=("Courier", 10))
        self.p_text.pack(fill='both', expand=True)

    def run_paging_simulation(self):
        try:
            num_frames = int(self.p_frames_entry.get().strip())
            if num_frames <= 0:
                raise ValueError
            ref_str = self.p_ref_entry.get().strip()
            self.p_references = [int(x) for x in ref_str.split()]
            if not self.p_references:
                raise ValueError
        except:
            messagebox.showerror("Error", "Invalid input. Use positive integer for frames and space-separated page numbers.")
            return

        algo = self.p_algo.get()
        self.p_sim = PagingSimulator(num_frames)
        self.p_steps = []
        self.p_fault_count = 0

        # Simulate all steps and store state after each access
        sim_copy = PagingSimulator(num_frames)
        for idx, page in enumerate(self.p_references):
            if algo == "OPTIMAL":
                fault = sim_copy.access_page(page, future_refs=self.p_references, current_index=idx, algorithm="OPTIMAL")
            else:
                fault = sim_copy.access_page(page, algorithm="LRU")
            if fault:
                self.p_fault_count += 1
            # store a copy of frames and fault flag
            self.p_steps.append((fault, sim_copy.frames.copy(), sim_copy.page_table.copy(), sim_copy.lru_queue.copy()))

        self.p_step_idx = -1
        self.p_btn_next.config(state='normal')
        self.p_btn_prev.config(state='disabled')
        self.p_btn_reset.config(state='normal')
        self.paging_next_step()  # show first step

    def paging_next_step(self):
        if self.p_step_idx + 1 >= len(self.p_steps):
            if self.p_steps:
                messagebox.showinfo("End", f"Simulation complete.\nTotal page faults: {self.p_fault_count}")
            self.p_btn_next.config(state='disabled')
            return
        self.p_step_idx += 1
        self.update_paging_display()
        self.p_btn_prev.config(state='normal')
        if self.p_step_idx == len(self.p_steps) - 1:
            self.p_btn_next.config(state='disabled')

    def paging_prev_step(self):
        if self.p_step_idx - 1 < 0:
            self.p_btn_prev.config(state='disabled')
            return
        self.p_step_idx -= 1
        self.update_paging_display()
        self.p_btn_next.config(state='normal')
        if self.p_step_idx == 0:
            self.p_btn_prev.config(state='disabled')

    def update_paging_display(self):
        fault, frames, pt, lru = self.p_steps[self.p_step_idx]
        self.p_text.delete(1.0, tk.END)
        self.p_text.insert(tk.END, f"Step {self.p_step_idx+1} of {len(self.p_steps)}\n")
        self.p_text.insert(tk.END, f"Accessing page: {self.p_references[self.p_step_idx]}\n")
        self.p_text.insert(tk.END, f"Page fault: {'YES' if fault else 'NO'}\n\n")
        self.p_text.insert(tk.END, "Current page frames:\n")
        self.p_text.insert(tk.END, "Frame | Page\n------+-----\n")
        for i, p in enumerate(frames):
            self.p_text.insert(tk.END, f"  {i:2}  |  {p if p is not None else '-'}\n")
        self.p_text.insert(tk.END, f"\nPage table: {pt}\n")
        self.p_text.insert(tk.END, f"LRU order (most recent last): {lru}\n")

    def paging_reset(self):
        self.p_step_idx = -1
        self.p_steps = []
        self.p_sim = None
        self.p_text.delete(1.0, tk.END)
        self.p_btn_next.config(state='disabled')
        self.p_btn_prev.config(state='disabled')
        self.p_btn_reset.config(state='disabled')

    # -------------------------------
    # Segmentation Tab
    # -------------------------------
    def setup_segmentation_tab(self):
        # Top controls
        frame_top = ttk.LabelFrame(self.seg_tab, text="Configuration", padding=5)
        frame_top.pack(fill='x', padx=5, pady=5)

        ttk.Label(frame_top, text="Total memory (bytes):").grid(row=0, column=0, sticky='w')
        self.s_mem_size = ttk.Entry(frame_top, width=10)
        self.s_mem_size.grid(row=0, column=1, sticky='w')
        self.s_mem_size.insert(0, "200")

        ttk.Label(frame_top, text="Allocation strategy:").grid(row=1, column=0, sticky='w')
        self.s_strategy = ttk.Combobox(frame_top, values=["first-fit", "best-fit"], state="readonly")
        self.s_strategy.grid(row=1, column=1, sticky='w')
        self.s_strategy.current(0)

        self.s_init_btn = ttk.Button(frame_top, text="Initialize Memory", command=self.init_segmentation)
        self.s_init_btn.grid(row=0, column=2, rowspan=2, padx=10)

        # Allocation/Deallocation
        frame_alloc = ttk.LabelFrame(self.seg_tab, text="Allocate / Deallocate", padding=5)
        frame_alloc.pack(fill='x', padx=5, pady=5)

        ttk.Label(frame_alloc, text="Segment name:").grid(row=0, column=0, sticky='w')
        self.s_name = ttk.Entry(frame_alloc, width=10)
        self.s_name.grid(row=0, column=1, padx=5)

        ttk.Label(frame_alloc, text="Size (bytes):").grid(row=0, column=2, sticky='w')
        self.s_size = ttk.Entry(frame_alloc, width=10)
        self.s_size.grid(row=0, column=3, padx=5)

        self.s_alloc_btn = ttk.Button(frame_alloc, text="Allocate", command=self.seg_allocate)
        self.s_alloc_btn.grid(row=0, column=4, padx=5)
        self.s_dealloc_btn = ttk.Button(frame_alloc, text="Deallocate", command=self.seg_deallocate)
        self.s_dealloc_btn.grid(row=0, column=5, padx=5)
        self.s_frag_btn = ttk.Button(frame_alloc, text="Random Fragmentation", command=self.seg_random_frag)
        self.s_frag_btn.grid(row=1, column=0, columnspan=6, pady=5)

        # Canvas for memory map
        frame_canvas = ttk.LabelFrame(self.seg_tab, text="Memory Map", padding=5)
        frame_canvas.pack(fill='both', expand=True, padx=5, pady=5)
        self.s_canvas = tk.Canvas(frame_canvas, bg='white', height=200)
        self.s_canvas.pack(fill='both', expand=True)

        # Info text
        self.s_info = scrolledtext.ScrolledText(frame_canvas, height=8, font=("Courier", 10))
        self.s_info.pack(fill='x', pady=5)

        self.seg_sim = None

    def init_segmentation(self):
        try:
            mem = int(self.s_mem_size.get().strip())
            if mem <= 0:
                raise ValueError
        except:
            messagebox.showerror("Error", "Memory size must be a positive integer.")
            return
        strat = self.s_strategy.get()
        self.seg_sim = SegmentationSimulator(mem, strat)
        self.update_seg_display()

    def seg_allocate(self):
        if self.seg_sim is None:
            messagebox.showwarning("Warning", "Initialize memory first.")
            return
        name = self.s_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Enter segment name.")
            return
        try:
            size = int(self.s_size.get().strip())
        except:
            messagebox.showerror("Error", "Size must be integer.")
            return
        ok, msg = self.seg_sim.allocate(name, size)
        if not ok:
            messagebox.showerror("Allocation failed", msg)
        else:
            self.update_seg_display()
            messagebox.showinfo("Success", msg)

    def seg_deallocate(self):
        if self.seg_sim is None:
            messagebox.showwarning("Warning", "Initialize memory first.")
            return
        name = self.s_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Enter segment name.")
            return
        ok, msg = self.seg_sim.deallocate(name)
        if not ok:
            messagebox.showerror("Deallocation failed", msg)
        else:
            self.update_seg_display()
            messagebox.showinfo("Success", msg)

    def seg_random_frag(self):
        if self.seg_sim is None:
            messagebox.showwarning("Warning", "Initialize memory first.")
            return
        # Perform 5 random operations to simulate fragmentation
        for _ in range(5):
            if random.choice([True, False]) or len(self.seg_sim.allocated) == 0:
                # allocate random segment
                name = f"auto_{random.randint(1000,9999)}"
                max_size = self.seg_sim.memory_size // 4
                size = random.randint(10, max_size)
                self.seg_sim.allocate(name, size)
            else:
                # deallocate a random existing segment
                if self.seg_sim.allocated:
                    name = random.choice(list(self.seg_sim.allocated.keys()))
                    self.seg_sim.deallocate(name)
        self.update_seg_display()
        messagebox.showinfo("Done", "Random fragmentation simulation completed.\nCheck memory map and fragmentation metric.")

    def update_seg_display(self):
        if self.seg_sim is None:
            return
        self.s_canvas.delete("all")
        blocks = self.seg_sim.get_memory_blocks()
        total_mem = self.seg_sim.memory_size
        # Draw memory map as horizontal bar
        width = self.s_canvas.winfo_width()
        if width < 10:
            width = 800
        height = 80
        self.s_canvas.config(height=height+20)
        y = 10
        x_start = 10
        x_end = width - 10
        total_width = x_end - x_start
        for start, size, typ, name in blocks:
            x0 = x_start + (start / total_mem) * total_width
            x1 = x_start + ((start + size) / total_mem) * total_width
            color = "#aaffaa" if typ == "free" else "#ffaaaa"
            self.s_canvas.create_rectangle(x0, y, x1, y+height, fill=color, outline="black")
            label = f"{name}" if name else f"FREE {size}B"
            self.s_canvas.create_text((x0+x1)/2, y+height/2, text=label, font=("Arial", 8))
        # Draw borders
        self.s_canvas.create_rectangle(x_start, y, x_end, y+height, outline="black", width=2)
        # Info text
        self.s_info.delete(1.0, tk.END)
        self.s_info.insert(tk.END, f"Memory size: {total_mem} bytes\n")
        self.s_info.insert(tk.END, f"Allocation strategy: {self.seg_sim.strategy}\n")
        total_free = sum(sz for _, sz in self.seg_sim.free_list)
        self.s_info.insert(tk.END, f"Total free: {total_free} bytes\n")
        largest_free = max((sz for _, sz in self.seg_sim.free_list), default=0)
        self.s_info.insert(tk.END, f"Largest free block: {largest_free} bytes\n")
        frag = self.seg_sim.fragmentation_metric()
        self.s_info.insert(tk.END, f"Fragmentation metric: {frag:.3f} (0 = none, 1 = high)\n")
        self.s_info.insert(tk.END, "\nAllocated segments:\n")
        for name, (start, size) in self.seg_sim.allocated.items():
            self.s_info.insert(tk.END, f"  {name}: start={start}, size={size}\n")

    # -------------------------------
    # Evaluator Tab
    # -------------------------------
    def setup_evaluator_tab(self):
        frame = ttk.LabelFrame(self.eval_tab, text="Parameters", padding=5)
        frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(frame, text="Number of page frames:").grid(row=0, column=0, sticky='w')
        self.e_frames = ttk.Entry(frame, width=10)
        self.e_frames.grid(row=0, column=1, padx=5)
        self.e_frames.insert(0, "3")

        ttk.Label(frame, text="Reference string (space-separated):").grid(row=1, column=0, sticky='w')
        self.e_ref = ttk.Entry(frame, width=50)
        self.e_ref.grid(row=1, column=1, columnspan=2, padx=5)
        self.e_ref.insert(0, "1 2 3 4 1 2 5 1 2 3 4 5")

        btn_eval = ttk.Button(frame, text="Compare Algorithms", command=self.run_evaluator)
        btn_eval.grid(row=2, column=1, pady=10)

        self.e_result = scrolledtext.ScrolledText(self.eval_tab, height=20, font=("Courier", 10))
        self.e_result.pack(fill='both', expand=True, padx=5, pady=5)

    def run_evaluator(self):
        try:
            num_frames = int(self.e_frames.get().strip())
            if num_frames <= 0:
                raise ValueError
            ref_str = self.e_ref.get().strip()
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

        self.e_result.delete(1.0, tk.END)
        self.e_result.insert(tk.END, "==== Page Replacement Evaluation ====\n\n")
        self.e_result.insert(tk.END, f"Number of frames: {num_frames}\n")
        self.e_result.insert(tk.END, f"Reference string: {references}\n\n")
        self.e_result.insert(tk.END, f"LRU page faults     : {faults_lru}\n")
        self.e_result.insert(tk.END, f"Optimal page faults : {faults_opt}\n\n")
        if faults_opt < faults_lru:
            self.e_result.insert(tk.END, "Optimal performs better (fewer faults).\n")
        elif faults_opt > faults_lru:
            self.e_result.insert(tk.END, "LRU performs better (unusual, but possible).\n")
        else:
            self.e_result.insert(tk.END, "Both algorithms have the same number of faults.\n")

# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualMemoryGUI(root)
    root.mainloop()
