import copy
import random
import heapq
from collections import deque
from typing import Optional

class JCB:
    def __init__(self, name: str, submit_time: int, burst_time: int, deadline: int = 0):
        self.name = name
        self.submit_time = submit_time
        self.burst_time = burst_time
        self.start_time = -1
        self.finish_time = 0
        self.turnaround_time = 0
        self.weighted_turnaround = 0.0
        self.status = 'W'
        self.deadline = deadline
        self.remaining_time = burst_time
    def settle_job(self, finish_time: int):
        self.finish_time = finish_time
        self.turnaround_time = finish_time - self.submit_time
        self.weighted_turnaround = self.turnaround_time / self.burst_time

    def __lt__(self, other):
        return self.deadline - self.remaining_time < other.deadline - other.remaining_time

def calculate_average(jobs: list[JCB]) -> tuple[float, float]:
    avg_turnaround = sum(job.turnaround_time for job in jobs) / len(jobs)
    avg_weighted = sum(job.weighted_turnaround for job in jobs) / len(jobs)
    return avg_turnaround, avg_weighted

HEAD_FMT = "{:<8} {:<8} {:<8} {:<8} {:<8} {:<8} {:<10}"
ROW_FMT = "{:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10.2f}"
def print_result(jobs: list[JCB], title: str):
    print(f"\n--- {title} 调度结果 ---")
    print('-' * 70)
    print(HEAD_FMT.format("作业名", "提交", "运行", "开始", "完成", "周转", "带权周转"))
    for job in jobs:
        print(ROW_FMT.format(
            job.name,
            job.submit_time,
            job.burst_time,
            job.start_time,
            job.finish_time,
            job.turnaround_time,
            job.weighted_turnaround
        ))
    avg_t, avg_wt = calculate_average(jobs)
    print('-' * 70)
    print(f"平均周转时间：{avg_t:.2f}")
    print(f"平均带权周转时间：{avg_wt:.2f}")

class Scheduler:
    def __init__(self, job_list: list[JCB]):
        self.jobs = copy.deepcopy(job_list)
        self.current_time = 0

    def reset_jobs(self) -> list[JCB]:
        return copy.deepcopy(self.jobs)
    def first_come_first_served(self):
        temp_jobs = sorted(self.reset_jobs(), key=lambda x: x.submit_time)
        finished_jobs: list[JCB] = []
        self.current_time = 0
        for job in temp_jobs:
            if self.current_time < job.submit_time:
                self.current_time = job.submit_time
            job.start_time = self.current_time
            job.status = 'R'
            job.settle_job(job.start_time + job.burst_time)
            job.status = 'F'
            self.current_time = job.finish_time
            finished_jobs.append(job)
        print_result(finished_jobs, "fcfs")
    def highest_response_next(self):
        pending_jobs = self.reset_jobs()
        finished_job = []
        self.current_time = 0
        while pending_jobs:
            available_jobs = [job for job in pending_jobs if job.submit_time <= self.current_time]
            if not available_jobs:
                self.current_time = min(job.submit_time for job in pending_jobs)
                continue
            selected_job = max(available_jobs,
                               key=lambda x: (self.current_time - x.submit_time) / x.burst_time + 1)
            selected_job.start_time = self.current_time
            selected_job.settle_job(selected_job.start_time + selected_job.burst_time)
            self.current_time = selected_job.finish_time
            finished_job.append(selected_job)
            pending_jobs.remove(selected_job)
        print_result(finished_job, "hrn")

    def multileved_feedback_queue(self):
        pending_jobs = deque(sorted(self.reset_jobs(), key=lambda x: x.submit_time))

        q1, q2, q3 = deque(), deque(), deque()
        MAX_SLICE = {1: 1, 2: 2, 3: 4}
        finished_job = []
        current_time = 0
        current_job: Optional[JCB] = None
        current_q_level = 0
        slice_executed = 0
        while pending_jobs or q1 or q2 or q3 or current_job:
            while pending_jobs and pending_jobs[0].submit_time <= current_time:
                q1.append(pending_jobs.popleft())

            if current_job and current_q_level > 1 and q1:
                if current_q_level == 2:
                    q2.append(current_job)
                elif current_q_level == 3:
                    q3.append(current_job)
                current_job = None
                slice_executed = 0
            
            if current_job is None:
                if q1:
                    current_job, current_q_level = q1.popleft(), 1
                elif q2:
                    current_job, current_q_level = q2.popleft(), 2
                elif q3:
                    current_job, current_q_level = q3.popleft(), 3
                slice_executed = 0
            
            if current_job is not None:
                if current_job.start_time == -1:
                    current_job.start_time = current_time
                current_job.remaining_time -= 1
                current_time += 1
                slice_executed += 1
                if current_job.remaining_time == 0:
                    current_job.settle_job(current_time)
                    finished_job.append(current_job)
                    current_job = None
                    slice_executed = 0
                else:
                    max_slice = MAX_SLICE[current_q_level]
                    if slice_executed >= max_slice:
                        if current_q_level == 1:
                            q2.append(current_job)
                        elif current_q_level == 2 or current_q_level == 3:
                            q3.append(current_job)
                        current_job = None
                        slice_executed = 0
            else:
                current_time += 1
        print_result(finished_job, "MFQ")
    
    def least_laxity_first(self):
        pending_jobs = deque(sorted(self.reset_jobs(), key=lambda x: x.submit_time))
        active_jobs: list[JCB] = []
        finished_jobs = []
        current_time = 0
        
        while pending_jobs or active_jobs:
            while pending_jobs and pending_jobs[0].submit_time <= current_time:
                heapq.heappush(active_jobs, pending_jobs.popleft())
            if not active_jobs:
                current_time = pending_jobs[0].submit_time
                continue
            current_job = heapq.heappop(active_jobs)
            if current_job.start_time == -1:
                current_job.start_time = current_time
            current_job.remaining_time -= 1
            current_time += 1
            if current_job.remaining_time == 0:
                current_job.settle_job(current_time)
                finished_jobs.append(current_job)
            else:
                heapq.heappush(active_jobs, current_job)
        print_result(finished_jobs, "LLF")


def generate_jobs(num: int = 50) -> list[JCB]:
    job_list = []
    cur_sub_time = 0
    for i in range(1, num + 1):
        cur_sub_time += random.randint(0, 4)
        runtime = random.randint(1, 20)
        deadline = cur_sub_time + runtime + random.randint(2, 10)
        job_list.append(JCB(f"P{i}", cur_sub_time, runtime, deadline))
        
    return job_list

if __name__ == "__main__":
    job_list = generate_jobs()
    scheduler = Scheduler(job_list)
    scheduler.first_come_first_served()
    scheduler.highest_response_next()
    scheduler.multileved_feedback_queue()
    scheduler.least_laxity_first()