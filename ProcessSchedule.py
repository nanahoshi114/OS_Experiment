import copy
import heapq
import random
from collections import deque
from typing import Callable, Optional
from contextlib import redirect_stdout

class PCB:
    def __init__(
        self,
        name: str,
        arrival: int,
        burst: int,
        priority: int,
        deadline: int = 0,
    ):
        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.priority = priority
        self.used_cpu = 0
        self.state = 'W'
        self.deadline = deadline if deadline else arrival + burst + 5
        self.remaining = burst

    def need_more(self) -> bool:
        return self.used_cpu < self.burst

    def laxity(self, current_time: int) -> int:
        return self.deadline - current_time - (self.burst - self.used_cpu)

    def clone(self) -> "PCB":
        p = PCB(self.name, self.arrival, self.burst, self.priority, self.deadline)
        p.used_cpu = self.used_cpu
        p.state = self.state
        p.remaining = self.remaining
        return p


PCB_HEAD = "{:<6} {:<6} {:<6} {:<6} {:<6} {:<6} {:<6} {:<6}"
PCB_ROW = "{:<6} {:<6} {:<6} {:<6} {:<6} {:<6} {:<6} {:<6}"


def print_snapshot(
    title: str,
    clock: int,
    running: Optional[PCB],
    ready_names: list[str],
    all_pcbs: list[PCB],
):
    print(f"\n--- {title} | 时刻 {clock} ---")
    run_name = running.name if running else "无"
    print(f"运行进程: {run_name}")
    print(f"就绪队列: {ready_names if ready_names else '[]'}")
    print(PCB_HEAD.format("进程", "优先数", "到达", "需运行", "已用CPU", "剩余", "截止", "状态"))
    for p in all_pcbs:
        remain = p.burst - p.used_cpu
        print(PCB_ROW.format(
            p.name, p.priority, p.arrival, p.burst,
            p.used_cpu, remain, p.deadline, p.state,
        ))


def admit_arrivals(
    pending: deque[PCB],
    ready: deque[PCB],
    clock: int,
    insert_fn: Callable[[deque[PCB], PCB], None],
):
    while pending and pending[0].arrival <= clock:
        proc = pending.popleft()
        proc.state = 'W'
        insert_fn(ready, proc)


def finish_slice(proc: PCB, ready: deque[PCB], insert_fn: Callable[[deque[PCB], PCB], None]):
    if proc.used_cpu >= proc.burst:
        proc.state = 'F'
    else:
        proc.priority -= 1
        proc.state = 'W'
        insert_fn(ready, proc)


class ProcessScheduler:
    def __init__(self, processes: list[PCB]):
        self.processes = processes

    def reset(self) -> list[PCB]:
        return [p.clone() for p in self.processes]

    def _run_time_slice_sim(
        self,
        title: str,
        select_fn: Callable[[deque[PCB], int], Optional[PCB]],
        insert_fn: Callable[[deque[PCB], PCB], None],
    ):
        all_pcbs = self.reset()
        pending = deque(sorted(all_pcbs, key=lambda x: x.arrival))
        ready: deque[PCB] = deque()
        clock = 0
        step = 0

        print_snapshot(title, clock, None, [], sorted(all_pcbs, key=lambda x: x.name))

        while pending or ready or any(p.state != 'F' for p in all_pcbs):
            admit_arrivals(pending, ready, clock, insert_fn)

            if not ready:
                if pending:
                    clock = pending[0].arrival
                    continue
                if all(p.state == 'F' for p in all_pcbs):
                    break
                continue

            selected = select_fn(ready, clock)
            if selected is None:
                break
            ready.remove(selected)
            selected.state = 'R'
            selected.used_cpu += 1
            clock += 1
            step += 1
            finish_slice(selected, ready, insert_fn)

            ready_names = [p.name for p in ready]
            print_snapshot(
                f"{title} 第{step}次调度",
                clock,
                selected,
                ready_names,
                sorted(all_pcbs, key=lambda x: x.name),
            )

        print(f"\n=== {title} 结束，共 {step} 次调度 ===\n")

    @staticmethod
    def _fcfs_insert(ready: deque[PCB], proc: PCB):
        ready.append(proc)

    @staticmethod
    def _fcfs_select(ready: deque[PCB], _clock: int) -> Optional[PCB]:
        return ready[0] if ready else None

    def first_come_first_served(self):
        self._run_time_slice_sim(
            "先来先服务(FCFS)",
            self._fcfs_select,
            self._fcfs_insert,
        )

    @staticmethod
    def _sjf_insert(ready: deque[PCB], proc: PCB):
        inserted = False
        for i, p in enumerate(ready):
            remain = proc.burst - proc.used_cpu
            if remain < p.burst - p.used_cpu:
                ready.insert(i, proc)
                inserted = True
                break
        if not inserted:
            ready.append(proc)

    @staticmethod
    def _sjf_select(ready: deque[PCB], _clock: int) -> Optional[PCB]:
        return min(ready, key=lambda p: (p.burst - p.used_cpu, p.arrival))

    def shortest_job_first(self):
        self._run_time_slice_sim(
            "短进程优先(SJF)",
            self._sjf_select,
            self._sjf_insert,
        )

    def multilevel_feedback_queue(self):
        pending = deque(sorted(self.reset(), key=lambda x: x.arrival))
        q1: deque[PCB] = deque()
        q2: deque[PCB] = deque()
        q3: deque[PCB] = deque()
        MAX_SLICE = {1: 1, 2: 2, 3: 4}
        finished: list[PCB] = []
        all_pcbs: list[PCB] = []
        clock = 0
        step = 0
        current: Optional[PCB] = None
        last_run: Optional[PCB] = None
        level = 0
        slice_cnt = 0

        def ready_names() -> list[str]:
            names = [p.name for p in q1] + [p.name for p in q2] + [p.name for p in q3]
            return names

        def all_process_list() -> list[PCB]:
            active = [p for p in all_pcbs if p.state != 'F']
            return sorted(active + finished, key=lambda x: x.name)

        print_snapshot("多级反馈队列(MFQ)", clock, None, [], [])

        while pending or q1 or q2 or q3 or current:
            while pending and pending[0].arrival <= clock:
                proc = pending.popleft()
                proc.state = 'W'
                q1.append(proc)
                all_pcbs.append(proc)

            if current is None:
                if q1:
                    current, level = q1.popleft(), 1
                elif q2:
                    current, level = q2.popleft(), 2
                elif q3:
                    current, level = q3.popleft(), 3
                slice_cnt = 0

            if current is None:
                if pending:
                    clock = pending[0].arrival
                    continue
                break

            current.state = 'R'
            current.used_cpu += 1
            clock += 1
            slice_cnt += 1
            step += 1
            last_run = current

            if current.used_cpu >= current.burst:
                current.state = 'F'
                finished.append(current)
                current = None
                slice_cnt = 0
            elif slice_cnt >= MAX_SLICE[level]:
                current.state = 'W'
                if level == 1:
                    q2.append(current)
                else:
                    q3.append(current)
                current = None
                slice_cnt = 0

            print_snapshot(
                f"多级反馈队列(MFQ) 第{step}次调度",
                clock,
                last_run,
                ready_names(),
                all_process_list(),
            )

        print(f"\n=== 多级反馈队列(MFQ) 结束，共 {step} 次调度 ===\n")

    def least_laxity_first(self):
        pending = deque(sorted(self.reset(), key=lambda x: x.arrival))
        ready_heap: list[tuple[int, int, str, PCB]] = []
        finished: list[PCB] = []
        all_pcbs: list[PCB] = []
        clock = 0
        step = 0
        current: Optional[PCB] = None
        last_run: Optional[PCB] = None

        def push_ready(proc: PCB):
            heapq.heappush(ready_heap, (proc.laxity(clock), proc.arrival, proc.name, proc))

        def ready_names() -> list[str]:
            return [item[3].name for item in sorted(ready_heap)]

        def all_process_list() -> list[PCB]:
            active = [p for p in all_pcbs if p.state != 'F']
            return sorted(active + finished, key=lambda x: x.name)

        print_snapshot("最小松弛度优先(LLF)", clock, None, [], [])

        while pending or ready_heap or current:
            while pending and pending[0].arrival <= clock:
                proc = pending.popleft()
                proc.state = 'W'
                push_ready(proc)
                all_pcbs.append(proc)

            if current is None and ready_heap:
                current = heapq.heappop(ready_heap)[3]

            if current is None:
                if pending:
                    clock = pending[0].arrival
                    continue
                break

            runner = current
            if ready_heap:
                best_lax = ready_heap[0][0]
                if best_lax < runner.laxity(clock):
                    runner.state = 'W'
                    push_ready(runner)
                    runner = heapq.heappop(ready_heap)[3]

            runner.state = 'R'
            runner.used_cpu += 1
            clock += 1
            step += 1
            last_run = runner

            if runner.used_cpu >= runner.burst:
                runner.state = 'F'
                finished.append(runner)
                current = None
            else:
                runner.state = 'W'
                push_ready(runner)
                current = None

            print_snapshot(
                f"最小松弛度优先(LLF) 第{step}次调度",
                clock,
                last_run,
                ready_names(),
                all_process_list(),
            )

        print(f"\n=== 最小松弛度优先(LLF) 结束，共 {step} 次调度 ===\n")


def read_processes(path: str = "ProcessFile.txt") -> list[PCB]:
    processes = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            name, arrival, burst = parts[0], int(parts[1]), int(parts[2])
            if len(parts) >= 5:
                priority, deadline = int(parts[3]), int(parts[4])
            elif len(parts) == 4:
                priority, deadline = int(parts[3]), arrival + burst + 5
            else:
                priority = random.randint(1, 10)
                deadline = arrival + burst + random.randint(2, 10)
            processes.append(PCB(name, arrival, burst, priority, deadline))
    return processes


if __name__ == "__main__":
    with open("ProcessScheduleOutput.txt", "w") as f:
        with redirect_stdout(f):
            processes = read_processes()
            scheduler = ProcessScheduler(processes)
            scheduler.first_come_first_served()
            scheduler.shortest_job_first()
            scheduler.multilevel_feedback_queue()
            scheduler.least_laxity_first()
