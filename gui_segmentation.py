"""
Segmentation Tab: allocate/deallocate, memory map canvas, fragmentation metric.
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
from segmentation import SegmentationSimulator

class SegmentationTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.sim = None
        self.setup_ui()

    def setup_ui(self):
        # Configuration frame
        config_frame = ttk.LabelFrame(self, text="Configuration", padding=5)
        config_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(config_frame, text="Total memory (bytes):").grid(row=0, column=0, sticky='w')
        self.mem_size_entry = ttk.Entry(config_frame, width=10)
        self.mem_size_entry.grid(row=0, column=1, sticky='w')
        self.mem_size_entry.insert(0, "200")

        ttk.Label(config_frame, text="Allocation strategy:").grid(row=1, column=0, sticky='w')
        self.strategy_combo = ttk.Combobox(config_frame, values=["first-fit", "best-fit"], state="readonly")
        self.strategy_combo.grid(row=1, column=1, sticky='w')
        self.strategy_combo.current(0)

        init_btn = ttk.Button(config_frame, text="Initialize Memory", command=self.init_memory)
        init_btn.grid(row=0, column=2, rowspan=2, padx=10)

        # Allocation / Deallocation frame
        alloc_frame = ttk.LabelFrame(self, text="Allocate / Deallocate", padding=5)
        alloc_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(alloc_frame, text="Segment name:").grid(row=0, column=0, sticky='w')
        self.name_entry = ttk.Entry(alloc_frame, width=10)
        self.name_entry.grid(row=0, column=1, padx=5)

        ttk.Label(alloc_frame, text="Size (bytes):").grid(row=0, column=2, sticky='w')
        self.size_entry = ttk.Entry(alloc_frame, width=10)
        self.size_entry.grid(row=0, column=3, padx=5)

        alloc_btn = ttk.Button(alloc_frame, text="Allocate", command=self.allocate_segment)
        alloc_btn.grid(row=0, column=4, padx=5)
        dealloc_btn = ttk.Button(alloc_frame, text="Deallocate", command=self.deallocate_segment)
        dealloc_btn.grid(row=0, column=5, padx=5)
        frag_btn = ttk.Button(alloc_frame, text="Random Fragmentation", command=self.random_fragmentation)
        frag_btn.grid(row=1, column=0, columnspan=6, pady=5)

        # Canvas for memory map
        canvas_frame = ttk.LabelFrame(self, text="Memory Map", padding=5)
        canvas_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self.canvas = tk.Canvas(canvas_frame, bg='white', height=200)
        self.canvas.pack(fill='both', expand=True)

        # Info text
        self.info_text = scrolledtext.ScrolledText(canvas_frame, height=8, font=("Courier", 10))
        self.info_text.pack(fill='x', pady=5)

    def init_memory(self):
        try:
            mem_size = int(self.mem_size_entry.get().strip())
            if mem_size <= 0:
                raise ValueError
        except:
            messagebox.showerror("Error", "Memory size must be a positive integer.")
            return
        strat = self.strategy_combo.get()
        self.sim = SegmentationSimulator(mem_size, strat)
        self.update_display()

    def allocate_segment(self):
        if self.sim is None:
            messagebox.showwarning("Warning", "Initialize memory first.")
            return
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Enter segment name.")
            return
        try:
            size = int(self.size_entry.get().strip())
        except:
            messagebox.showerror("Error", "Size must be integer.")
            return
        ok, msg = self.sim.allocate(name, size)
        if not ok:
            messagebox.showerror("Allocation failed", msg)
        else:
            self.update_display()
            messagebox.showinfo("Success", msg)

    def deallocate_segment(self):
        if self.sim is None:
            messagebox.showwarning("Warning", "Initialize memory first.")
            return
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Enter segment name.")
            return
        ok, msg = self.sim.deallocate(name)
        if not ok:
            messagebox.showerror("Deallocation failed", msg)
        else:
            self.update_display()
            messagebox.showinfo("Success", msg)

    def random_fragmentation(self):
        if self.sim is None:
            messagebox.showwarning("Warning", "Initialize memory first.")
            return
        for _ in range(5):
            if random.choice([True, False]) or len(self.sim.allocated) == 0:
                name = f"auto_{random.randint(1000, 9999)}"
                max_size = self.sim.memory_size // 4
                size = random.randint(10, max_size)
                self.sim.allocate(name, size)
            else:
                if self.sim.allocated:
                    name = random.choice(list(self.sim.allocated.keys()))
                    self.sim.deallocate(name)
        self.update_display()
        messagebox.showinfo("Done", "Random fragmentation simulation completed.\nCheck memory map and fragmentation metric.")

    def update_display(self):
        if self.sim is None:
            return
        self.canvas.delete("all")
        blocks = self.sim.get_memory_blocks()
        total_mem = self.sim.memory_size

        width = self.canvas.winfo_width()
        if width < 10:
            width = 800
        height = 80
        self.canvas.config(height=height+20)
        y = 10
        x_start = 10
        x_end = width - 10
        total_width = x_end - x_start

        for start, size, typ, name in blocks:
            x0 = x_start + (start / total_mem) * total_width
            x1 = x_start + ((start + size) / total_mem) * total_width
            color = "#aaffaa" if typ == "free" else "#ffaaaa"
            self.canvas.create_rectangle(x0, y, x1, y+height, fill=color, outline="black")
            label = f"{name}" if name else f"FREE {size}B"
            self.canvas.create_text((x0+x1)/2, y+height/2, text=label, font=("Arial", 8))

        self.canvas.create_rectangle(x_start, y, x_end, y+height, outline="black", width=2)

        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, f"Memory size: {total_mem} bytes\n")
        self.info_text.insert(tk.END, f"Allocation strategy: {self.sim.strategy}\n")
        total_free = sum(sz for _, sz in self.sim.free_list)
        self.info_text.insert(tk.END, f"Total free: {total_free} bytes\n")
        largest_free = max((sz for _, sz in self.sim.free_list), default=0)
        self.info_text.insert(tk.END, f"Largest free block: {largest_free} bytes\n")
        frag = self.sim.fragmentation_metric()
        self.info_text.insert(tk.END, f"Fragmentation metric: {frag:.3f} (0 = none, 1 = high)\n")
        self.info_text.insert(tk.END, "\nAllocated segments:\n")
        for name, (start, size) in self.sim.allocated.items():
            self.info_text.insert(tk.END, f"  {name}: start={start}, size={size}\n")
