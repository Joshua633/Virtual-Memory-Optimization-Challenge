"""
Paging Simulator: demand paging, LRU and Optimal replacement.
"""
from typing import List, Optional, Dict, Tuple

class PagingSimulator:
    def __init__(self, num_frames: int):
        self.num_frames = num_frames
        self.frames: List[Optional[int]] = [None] * num_frames
        self.page_table: Dict[int, int] = {}
        self.lru_queue: List[int] = []

    def _update_lru(self, page: int):
        if page in self.lru_queue:
            self.lru_queue.remove(page)
        self.lru_queue.append(page)

    def _get_optimal_victim(self, future_refs: List[int], current_index: int) -> int:
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

    def access_page(self, page: int, future_refs: Optional[List[int]] = None,
                    current_index: int = -1, algorithm: str = 'LRU') -> bool:
        """
        Simulate a single page access.
        Returns True if page fault occurred, False otherwise.
        """
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
            victim_frame = self.page_table.pop(victim_page)
            self.frames[victim_frame] = page
            self.page_table[page] = victim_frame
            self._update_lru(page)
            return True
        elif algorithm == 'OPTIMAL':
            if future_refs is None or current_index == -1:
                raise ValueError("Optimal requires future references and index")
            victim_frame = self._get_optimal_victim(future_refs, current_index)
            victim_page = self.frames[victim_frame]
            del self.page_table[victim_page]
            self.frames[victim_frame] = page
            self.page_table[page] = victim_frame
            self._update_lru(page)
            return True
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

    def reset(self):
        self.frames = [None] * self.num_frames
        self.page_table = {}
        self.lru_queue = []
