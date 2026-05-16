import copy
import random

class JCB:
    def __init__(self, name: str, submit_time: int, burst_time: int):
        self.name = name
        self.submit_time = submit_time
        self.burst_time = burst_time
        self.start_time = 0
        self.finish_time = 0
        self.turnaround_time = 0
        self.weighted_turnaround = 0.0
        self.status = 'W'

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

    def first_come_first_served(self):
        temp_jobs = sorted(self.jobs, key=lambda x: x.submit_time)
        finished_jobs: list[JCB] = []
        self.current_time = 0
        for job in temp_jobs:
            if self.current_time < job.submit_time:
                self.current_time = job.submit_time
            job.start_time = self.current_time
            job.status = 'R'
            job.finish_time = job.start_time + job.burst_time
            job.turnaround_time = job.finish_time - job.submit_time
            job.weighted_turnaround = job.turnaround_time / job.burst_time
            job.status = 'F'
            self.current_time = job.finish_time
            finished_jobs.append(job)
        print_result(finished_jobs, "fcfs")
    def highest_response_next(self):
        pending_jobs = copy.deepcopy(self.jobs)
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
            selected_job.finish_time = selected_job.start_time + selected_job.burst_time
            selected_job.turnaround_time = selected_job.finish_time - selected_job.submit_time
            selected_job.weighted_turnaround = selected_job.turnaround_time / selected_job.burst_time
            self.current_time = selected_job.finish_time
            finished_job.append(selected_job)
            pending_jobs.remove(selected_job)
        print_result(finished_job, "hrn")

def generate_jobs(num: int = 50) -> list[JCB]:
    job_list = []
    cur_sub_time = 0
    for i in range(1, num + 1):
        cur_sub_time += random.randint(0, 4)
        runtime = random.randint(1, 20)
        job_list.append(JCB(f"P{i}", cur_sub_time, runtime))
    return job_list

if __name__ == "__main__":
    job_list = generate_jobs()
    scheduler = Scheduler(job_list)
    scheduler.first_come_first_served()
    scheduler.highest_response_next()