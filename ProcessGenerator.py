import random

def generate_processes(num: int = 50):
    cur_arrival = 0
    with open("ProcessFile.txt", "w") as f:
        for i in range(1, num + 1):
            cur_arrival += random.randint(0, 4)
            burst = random.randint(1, 20)
            priority = random.randint(1, 10)
            deadline = cur_arrival + burst + random.randint(2, 10)
            f.write(f"P{i} {cur_arrival} {burst} {priority} {deadline}\n")

if __name__ == "__main__":
    print("输入要生成的进程个数：")
    n = int(input())
    generate_processes(n)