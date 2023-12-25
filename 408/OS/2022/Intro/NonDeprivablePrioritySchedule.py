import random
import plotly.express as px
import pandas as pd


def generate_system_condition():
    cpu_count = 1
    device_count = random.randint(2, 4)
    return cpu_count, device_count


def generate_task(cpu_count, device_count):
    assert cpu_count is 1
    # todo:我不确定多核的非剥夺调度是不是也是这样
    procedures_count = random.randint(6, 12)
    procedures = []
    prev_procedure = None
    for i in range(0, procedures_count):
        procedure_type = random.randint(0, device_count)
        if prev_procedure is None:
            prev_procedure = procedure_type
        else:
            while prev_procedure is procedure_type:
                procedure_type = random.randint(0, device_count)
        procedure_span = int(random.random() * 100)
        procedure_span -= (procedure_span % 10)
        procedure_span = max(10, procedure_span)
        procedures.append([procedure_type, procedure_span])
    return procedures


def finished(tasks):
    for task in tasks:
        if len(task) > 0:
            return False
    return True


def schedule_solution(tasks, devices_busy, task_countdowns, task_on_devices, solution, time_stamp, min_wait=None):
    if min_wait is None:
        min_wait = 9999
    for i in range(0, len(tasks)):
        if len(tasks[i]) > 0:
            if task_countdowns[i] is 0:
                if devices_busy[tasks[i][0][0]] is None:
                    devices_busy[tasks[i][0][0]] = i
                    task_on_devices[i] = tasks[i][0][0]
                    task_countdowns[i] = tasks[i][0][1]
                    if task_countdowns[i] < min_wait:
                        min_wait = task_countdowns[i]
                    solution.append([i, time_stamp, tasks[i].pop(0)])
                else:
                    task_countdowns[i] = min_wait
            else:
                continue
        else:
            continue


def arranged(tasks, task_countdowns):
    for i in range(0, len(tasks)):
        if len(tasks[i]) > 0 and task_countdowns[i] is 0:
            return False
    return True


def least_but_not_zero(tc):
    tc_copy = tc.copy()
    while 0 in tc_copy:
        tc_copy.remove(0)
    return min(tc_copy)


def keep_running(tasks, cpu_count, device_count):
    devices_busy = [None] * (cpu_count + device_count)
    task_countdowns = [0] * len(tasks)
    task_on_devices = [None] * len(tasks)
    min_wait = None
    solution = []
    time_stamp = 0
    while not finished(tasks):
        if not arranged(tasks, task_countdowns):
            schedule_solution(tasks, devices_busy, task_countdowns, task_on_devices, solution, time_stamp, min_wait)
        else:
            if 0 in task_countdowns:
                next_time = least_but_not_zero(task_countdowns)
            else:
                next_time = min(task_countdowns)
            time_stamp += next_time
            for i in range(0, len(tasks)):
                task_countdowns[i] = max(0, task_countdowns[i] - next_time)
                if task_countdowns[i] is 0:
                    if task_on_devices[i] is not None:
                        # noinspection PyTypeChecker
                        devices_busy[task_on_devices[i]] = None
                    task_on_devices[i] = None
            min_wait = None
            for i in range(0, len(tasks)):
                if task_countdowns[i] is not 0:
                    if min_wait is None or task_countdowns[i] < min_wait:
                        min_wait = task_countdowns[i]
    return solution


if __name__ is '__main__':
    cc, dc = generate_system_condition()
    dc = 2
    t1 = generate_task(cc, dc)
    t2 = generate_task(cc, dc)
    t3 = generate_task(cc, dc)
    ts = [t1, t2, t3]
    s = keep_running(ts, cc, dc)
    s_list = []
    for task in s:
        s_list.append(
            dict(
                Task=str(task[0]),
                Start=task[1],
                Finish=task[1] + task[2][1],
                Resource=str(task[2][0]),
                Delta=task[2][1]

            )
        )
    df = pd.DataFrame(
        s_list
    )

    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color="Resource")
    fig.update_yaxes(autorange="reversed")  # otherwise tasks are listed from the bottom up
    fig.layout.xaxis.type = 'linear'
    for d in fig.data:
        f = df['Resource'] == d.name
        d.x = df[f]['Delta'].tolist()
    fig.show()
    print('Done')
    # todo:我用的是优先级分配，没有用到队列
