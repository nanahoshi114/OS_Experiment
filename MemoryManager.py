from dataclasses import dataclass
from typing import Any, Optional



class Block:
    def __init__(self, id: int, size: int, start: int) -> None:
        self.id = id
        self.size = size
        self.start = start
        self.next: Optional[Block] = None

class MemoryManager:
    def __init__(self, total_size: int, algo: int):
        self.memory_head = Block(-1, total_size, 0)
        self.algo = algo
    
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
        best_block = self.memory_head
        if self.algo == 0:
            while best_block is not None:
                if best_block.id == -1 and best_block.size >= size:
                    break
                best_block = best_block.next
        else:
            min_size = int(1e9)
            cur_block = self.memory_head
            while cur_block is not None:
                if cur_block.id == -1 and cur_block.size >= size and cur_block.size < min_size:
                    min_size = cur_block.size
                    best_block = cur_block
                cur_block = cur_block.next
        
        action = f"作业{job_id} 申请 {size}KB"
        if best_block is None:
            print(f"{action} | 失败：内存不足！")
            return
        if best_block.size > size:
            new_free_block = Block(-1, best_block.size - size, best_block.start + size)
            best_block.id = job_id
            best_block.size -= size
            new_free_block.next = best_block.next
            best_block.next = new_free_block
        else:
            best_block.id = job_id
    
    def deallocate(self, job_id: int):
        action = f"作业{job_id} 释放"
        cur_block = self.memory_head
        while cur_block is not None:
            if cur_block.id == job_id:
                action += f" {cur_block.size}KB"
                cur_block.id = -1

                next_block = cur_block.next
                if next_block is not None and next_block.id == -1:
                    cur_block.size += next_block.size
                    cur_block.next = next_block.next
                
                if cur_block is not self.memory_head:
                    pre_block = self.memory_head
                    while pre_block is not None and pre_block.next is not cur_block:
                        pre_block = pre_block.next
                    if pre_block is not None and pre_block.id == -1:
                        pre_block.size += cur_block.size
                        pre_block.next = cur_block.next
                self.print_free_chain(action)
                return
        print(f"{action} | 未找到作业{job_id}！")
    