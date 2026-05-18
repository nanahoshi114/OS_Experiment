from dataclasses import dataclass
from typing import Any, Optional



class Block:
    def __init__(self, id: int, size: int, start: int) -> None:
        self.id = id
        self.size = size
        self.start = start
        self.next: Optional[Block] = None
ALGO_SET = {
    "First Fit",
    "Best Fit",
    "Worst Fit",
    "Next Fit"
}
class MemoryManager:
    def __init__(self, total_size: int, algo_str: str):
        self.memory_head = Block(-1, total_size, 0)
        self.last_search_block: Optional[Block] = None
        self.algo: str = algo_str
        if algo_str not in ALGO_SET:
            raise ValueError("Error: algorithm name undefined!")
    
    def choose_block(self, size: int) -> Optional[Block]:
        cur_block = self.memory_head
        if self.algo == 'First Fit':
            while cur_block is not None:
                if cur_block.id == -1 and cur_block.size >= size:
                    break
                cur_block = cur_block.next
            return cur_block
        elif self.algo == 'Best Fit':
            best_block = None
            min_size = int(1e9)
            while cur_block is not None:
                if cur_block.id == -1 and cur_block.size >= size and cur_block.size < min_size:
                    min_size = cur_block.size
                    best_block = cur_block
                cur_block = cur_block.next
            return best_block
        elif self.algo == 'Worst Fit':
            best_block = None
            max_size = -1
            while cur_block is not None:
                if cur_block.id == -1 and cur_block.size >= size and cur_block.size > max_size:
                    max_size = cur_block.size
                    best_block = cur_block
                cur_block = cur_block.next
            return best_block
        elif self.algo == 'Next Fit':
            start_block = self.last_search_block if self.last_search_block is not None else self.memory_head
            cur_block = start_block
            while True:
                if cur_block.id == -1 and cur_block.size >= size:
                    return cur_block
                cur_block = cur_block.next
                if cur_block is None:
                    cur_block = self.memory_head
                if cur_block == start_block:
                    return None
        return None

    def print_free_chain(self, action: str):
        free_blocks = []
        cur_block = self.memory_head
        while cur_block is not None:
            if cur_block.id == -1:
                free_blocks.append(f"[首地址：{cur_block.start}，大小：{cur_block.size}KB]")
            cur_block = cur_block.next
        chain_str = " -> ".join(free_blocks) if free_blocks else "无可用空闲区"
        print(f"{action:<18} | 空闲链：{chain_str}")

    def allocate(self, job_id: int, size: int):
        best_block = self.choose_block(size)
        action = f"作业{job_id} 申请 {size}KB"
        if best_block is None:
            print(f"{action:<18} | 失败：内存不足！")
            return
        if best_block.size > size:
            new_free_block = Block(-1, best_block.size - size, best_block.start + size)
            best_block.id = job_id
            best_block.size = size
            new_free_block.next = best_block.next
            best_block.next = new_free_block
            if self.algo == 'Next Fit':
                self.last_search_block = new_free_block
        else:
            best_block.id = job_id
            if self.algo == 'Next Fit':
                self.last_search_block = best_block.next if best_block.next is not None else self.memory_head
        self.print_free_chain(action)

    def deallocate(self, job_id: int):
        action = f"作业{job_id} 释放"
        cur_block = self.memory_head

        while cur_block is not None:
            if cur_block.id == job_id:
                break
            cur_block = cur_block.next
        if cur_block is None:
            print(f"{action:<18} | 未找到作业{job_id}!")
            return
        action += f" {cur_block.size}KB"
        cur_block.id = -1
        next_block = cur_block.next
        if next_block is not None and next_block.id == -1:
            cur_block.size += next_block.size
            cur_block.next = next_block.next
            if self.algo == 'Next Fit' and self.last_search_block == next_block:
                self.last_search_block = cur_block
        
        if cur_block is not self.memory_head:
            pre_block = self.memory_head
            while pre_block is not None and pre_block.next is not cur_block:
                pre_block = pre_block.next
            if pre_block is not None and pre_block.id == -1:
                pre_block.size += cur_block.size
                pre_block.next = cur_block.next
                if self.algo == 'Next Fit' and self.last_search_block == cur_block:
                    self.last_search_block = pre_block
        self.print_free_chain(action)

def run_simulation(algo_name):
    print(f"========== {algo_name} ==========")
    mm = MemoryManager(640, algo_name)
    for job, size in [(1,130), (2,60), (3,100)]: 
        mm.allocate(job, size)
        
    mm.deallocate(2)
    mm.allocate(4, 200)
    mm.deallocate(3)
    mm.deallocate(1)
    
    for job, size in [(5,140), (6,60), (7,50), (8,60)]: 
        mm.allocate(job, size)
        
    print("-" * 65 + "\n")
if __name__ == "__main__":
    for algo in ['First Fit', 'Best Fit', 'Worst Fit', 'Next Fit']:
        run_simulation(algo)