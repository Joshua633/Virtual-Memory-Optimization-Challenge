"""
Segmentation Simulator: first-fit / best-fit allocation, fragmentation metric.
"""
import sys
from typing import List, Tuple, Dict

class SegmentationSimulator:
    def __init__(self, memory_size: int, strategy: str = 'first-fit'):
        self.memory_size = memory_size
        self.strategy = strategy.lower()
        self.free_list: List[Tuple[int, int]] = [(0, memory_size)]
        self.allocated: Dict[str, Tuple[int, int]] = {}

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

    def allocate(self, name: str, size: int) -> Tuple[bool, str]:
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
            return False, f"Unknown strategy: {self.strategy}"

        if best_idx == -1:
            return False, f"Not enough contiguous memory for {size} bytes."

        start, free_sz = self.free_list.pop(best_idx)
        self.allocated[name] = (start, size)
        if free_sz > size:
            self.free_list.append((start + size, free_sz - size))
        self._merge_free_blocks()
        return True, f"Segment '{name}' allocated."

    def deallocate(self, name: str) -> Tuple[bool, str]:
        if name not in self.allocated:
            return False, f"Segment '{name}' not found."
        start, size = self.allocated.pop(name)
        self.free_list.append((start, size))
        self._merge_free_blocks()
        return True, f"Segment '{name}' deallocated."

    def get_memory_blocks(self) -> List[Tuple[int, int, str, str]]:
        """Returns list of (start, size, type, name) for drawing."""
        blocks = []
        for name, (start, size) in self.allocated.items():
            blocks.append((start, size, "allocated", name))
        for start, size in self.free_list:
            blocks.append((start, size, "free", ""))
        blocks.sort(key=lambda x: x[0])
        return blocks

    def fragmentation_metric(self) -> float:
        total_free = sum(sz for _, sz in self.free_list)
        if total_free == 0:
            return 0.0
        largest_free = max((sz for _, sz in self.free_list), default=0)
        return 1 - (largest_free / total_free)
