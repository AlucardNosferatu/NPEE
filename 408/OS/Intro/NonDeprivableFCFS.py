from NonDeprivablePrioritySchedule import generate_system_condition, generate_task
import pandas as pd
import plotly.express as px


def finished(tasks, sys_st_queue):
    for task in tasks:
        if len(task) > 0:
            return False
    for dev in sys_st_queue:
        if dev['status'] is 'EXEC':
            return False
    return True


# 只负责倒计时，不改变状态
def time_step(sys_st_queue):
    countdown = 0
    for dev in sys_st_queue:
        if dev['countdown'] != 0:
            if countdown == 0 or countdown > dev['countdown']:
                countdown = dev['countdown']
    for i in range(0, len(sys_st_queue)):
        if sys_st_queue[i]['status'] is 'EXEC':
            sys_st_queue[i]['countdown'] -= countdown
    return countdown


# 只负责队中调度，不负责“装弹”
# 根据状态和倒计时处理
def schedule(sys_st_queue, tq_relation):
    for dev in sys_st_queue:
        if dev['status'] is 'EXEC':
            if dev['countdown'] == 0:
                dev['status'] = 'IDLE'
                tq_relation[dev['user']] = None
                dev['user'] = None
        if dev['status'] is 'IDLE':
            if len(dev['queue']) > 0:
                process = dev['queue'].pop(0)
                dev['status'] = 'EXEC'
                dev['user'] = process['tid']
                dev['countdown'] = process['process'][1]


# 只负责装弹，不负责调度
# tasks不保存时态（与当前上下文相关的）信息
# 注意：一个任务只能排一个队
def load_queue(tasks, sys_st_queue, tq_relation):
    for i in range(0, len(tasks)):
        if tq_relation[i] is None:
            task = tasks[i]
            if len(task) > 0:
                first_process = task[0]
                process_type = first_process[0]
                tq_relation[i] = process_type
                sys_st_queue[process_type]['queue'].append({'tid': i, 'process': task.pop(0)})


def first_come_first_served(tasks, sys_st_queue):
    time_stamp = 0
    info_list = []
    tq_relation = []
    for i in range(0, len(tasks)):
        tq_relation.append(None)
    while not finished(tasks, sys_st_queue):
        load_queue(tasks, sys_st_queue, tq_relation)
        time_span = time_step(sys_st_queue)
        time_stamp += time_span
        schedule(sys_st_queue, tq_relation)
        print('time', time_stamp)
        print_sys_status(sys_st_queue)
        solution_logger(time_stamp, sys_st_queue, info_list)
    return info_list


def print_sys_status(sys_st_queue):
    for i in range(0, len(sys_st_queue)):
        dev = sys_st_queue[i]
        print('dev_id', i, 'status', dev['status'], 'user', dev['user'], 'countdown', dev['countdown'])


def solution_logger(time_stamp, sys_st_queue, info_list):
    for i in range(0, len(sys_st_queue)):
        dev = sys_st_queue[i]
        if dev['user'] is not None:
            info = dict(
                Task=str(dev['user']),
                Start=time_stamp,
                Finish=time_stamp + dev['countdown'],
                Resource=str(i),
                Delta=dev['countdown']

            )
            info_list.append(info)


if __name__ is '__main__':
    cc, dc = generate_system_condition()
    dc = 2
    dev_list = []
    for fuck in range(0, cc + dc):
        dev_dict = {'user': None, 'countdown': 0, 'status': 'IDLE', 'queue': []}
        dev_list.append(dev_dict)
    # ts = []
    # ts_copy = []
    # for fuck in range(0, 3):
    #     t = generate_task(cc, dc)
    #     ts.append(t)
    #     ts_copy.append(t.copy())
    ts = [
        [[2, 10], [1, 40], [0, 50], [0, 40], [1, 10], [1, 10], [0, 30], [1, 60]],
        [[1, 20], [0, 10], [2, 50], [0, 10], [0, 50], [0, 10], [2, 90], [2, 50], [2, 10], [0, 40], [2, 10]],
        [[2, 80], [1, 50], [1, 90], [1, 80], [1, 50], [1, 70]]
    ]
    i_list = first_come_first_served(ts, dev_list)
    df = pd.DataFrame(
        i_list
    )

    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color="Resource")
    fig.update_yaxes(autorange="reversed")  # otherwise tasks are listed from the bottom up
    fig.layout.xaxis.type = 'linear'
    for d in fig.data:
        f = df['Resource'] == d.name
        d.x = df[f]['Delta'].tolist()
    fig.show()
    print('Done')
