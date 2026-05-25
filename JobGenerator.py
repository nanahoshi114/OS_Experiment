import random

def generate_jobs(num: int = 50):
    cur_sub_time = 0
    with open("JobFile.txt", "w") as f:
        for i in range(1, num + 1):
            cur_sub_time += random.randint(0, 4)
            runtime = random.randint(1, 20)
            f.write(f"P{i} {cur_sub_time} {runtime}\n")

if __name__ == "__main__":
    print("输入要生成的任务个数：")
    n = int(input())
    generate_jobs(n)