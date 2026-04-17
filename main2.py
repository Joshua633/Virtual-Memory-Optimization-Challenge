#!/usr/bin/env python3
"""
Virtual Memory Management Tool - Entry Point
"""
import tkinter as tk
from gui_main import VirtualMemoryGUI

def main():
    root = tk.Tk()
    app = VirtualMemoryGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
