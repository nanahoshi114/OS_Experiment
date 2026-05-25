import copy
from collections import deque

class JCB:
    def __init__(self, name: str, submit_time: int, burst_time: int):
        self.name = name
        self.submit_time = submit_time
        self.burst_time = burst_time
        self.start_time = -1
        self.finish_time = 0
        self.turnaround_time = 0
        self.weighted_turnaround = 0.0
        self.status = 'W'
        self.remaining_time = burst_time
    def settle_job(self, finish_time: int):
        self.finish_time = finish_time
        self.turnaround_time = finish_time - self.submit_time
        self.weighted_turnaround = self.turnaround_time / self.burst_time

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

    def multilevel_queue(self):
        """多级队列：按运行时间分入不同队列，高优先级队列全部完成后才调度低优先级队列，队列内 FCFS。"""
        temp_jobs = sorted(self.reset_jobs(), key=lambda x: x.submit_time)
        q1, q2, q3 = [], [], []
        for job in temp_jobs:
            if job.burst_time <= 5:
                q1.append(job)
            elif job.burst_time <= 12:
                q2.append(job)
            else:
                q3.append(job)
        finished_jobs: list[JCB] = []
        self.current_time = 0
        for queue in (q1, q2, q3):
            for job in sorted(queue, key=lambda x: x.submit_time):
                if self.current_time < job.submit_time:
                    self.current_time = job.submit_time
                job.start_time = self.current_time
                job.status = 'R'
                job.settle_job(self.current_time + job.burst_time)
                job.status = 'F'
                self.current_time = job.finish_time
                finished_jobs.append(job)
        print_result(finished_jobs, "多级队列")

    def priority_scheduling(self):
        """优先级调度：优先数越大越先运行（短作业赋予更高优先数）。"""
        pending_jobs = self.reset_jobs()
        finished_jobs: list[JCB] = []
        self.current_time = 0
        while pending_jobs:
            available = [j for j in pending_jobs if j.submit_time <= self.current_time]
            if not available:
                self.current_time = min(j.submit_time for j in pending_jobs)
                continue
            selected = max(available, key=lambda x: 21 - x.burst_time)
            if self.current_time < selected.submit_time:
                self.current_time = selected.submit_time
            selected.start_time = self.current_time
            selected.status = 'R'
            selected.settle_job(self.current_time + selected.burst_time)
            selected.status = 'F'
            self.current_time = selected.finish_time
            finished_jobs.append(selected)
            pending_jobs.remove(selected)
        print_result(finished_jobs, "优先级")


def read_jobs() -> list[JCB]:
    job_list = []
    with open("JobFile.txt", "r") as f:
        for line in f:
            name, sub_time, run_time = line.split()
            job_list.append(JCB(name, int(sub_time), int(run_time)))
    return job_list

if __name__ == "__main__":
    job_list = read_jobs()
    scheduler = Scheduler(job_list)
    scheduler.first_come_first_served()
    scheduler.highest_response_next()
    scheduler.multilevel_queue()
    scheduler.priority_scheduling()