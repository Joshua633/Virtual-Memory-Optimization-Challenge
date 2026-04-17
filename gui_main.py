"""
Main GUI window with notebook (tabs) and integration of all modules.
"""
import tkinter as tk
from tkinter import ttk
from gui_paging import PagingTab
from gui_segmentation import SegmentationTab
from gui_evaluator import EvaluatorTab

class VirtualMemoryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Memory Management Tool")
        self.root.geometry("900x700")

        style = ttk.Style()
        style.theme_use('clam')

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Create and add tabs
        self.paging_tab = PagingTab(self.notebook)
        self.seg_tab = SegmentationTab(self.notebook)
        self.eval_tab = EvaluatorTab(self.notebook)

        self.notebook.add(self.paging_tab, text="Paging Simulation")
        self.notebook.add(self.seg_tab, text="Segmentation")
        self.notebook.add(self.eval_tab, text="Page Replacement Evaluator")
