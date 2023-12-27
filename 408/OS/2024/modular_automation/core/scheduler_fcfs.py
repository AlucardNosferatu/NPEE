import random
import threading
import time
import uuid

from kill_thread import kill_thread

from core.flow_chart import finished_tasks, suspend_handle, debug, run_flow_chart, singleton_modules

running_tasks = {}
workers_count = 16
waiting_tasks = {}
waiting_order = []
rt_lock = threading.Lock()


# task = [task_id, hook_script, map_json, involved_modules, prerequisite]
# r_task = [task_id, hook_script, map_json, involved_modules, prerequisite, running_thread]


def process_queued_task():
    while True:
        if debug:
            print('当前队列状况，执行:{}，等待:{}'.format(len(running_tasks.keys()), len(waiting_tasks.keys())))
        rt_lock.acquire()
        check_waiting_task()
        remove_finished_task()
        rt_lock.release()
        time.sleep(0.25)


def check_waiting_task():
    if len(running_tasks.keys()) < workers_count:
        if len(waiting_tasks.keys()) > 0:
            task_id = waiting_order.pop(0)
            task = waiting_tasks.pop(task_id)
            runnable = True
            runnable = check_conflict_task(runnable, task)
            if runnable:
                execute_runnable_task(task=task)
            else:
                create_waiting_task(task=task)


def check_conflict_task(runnable, task):
    involved_modules = task[3]
    for r_task_id in running_tasks.keys():
        r_task = running_tasks[r_task_id]
        r_involved_modules = r_task[3]
        common_modules = list(set(involved_modules).intersection(set(r_involved_modules)))
        for m in common_modules:
            if m in singleton_modules:
                print('任务:{}与执行中任务:{}存在资源冲突，冲突模块为:{}'.format(task[0], r_task[0], m))
                runnable = False
                break
        if not runnable:
            break
    return runnable


def execute_runnable_task(task):
    task_id = task[0]
    running_thread = threading.Thread(target=run_flow_chart, args=tuple(task))
    task.append(running_thread)
    running_tasks[task_id] = task
    running_thread.start()
    print('任务开始执行，id:{}'.format(task_id))


def create_waiting_task(task):
    task_id = task[0]
    waiting_tasks[task_id] = task
    waiting_order.append(task_id)
    print('任务送入等待队列，id:{}'.format(task_id))


def remove_finished_task():
    while len(finished_tasks) > 0:
        task_id = finished_tasks.pop(0)
        if task_id in suspend_handle.keys():
            status = suspend_handle.pop(task_id)
            print('任务完成，最后执行状态:{}'.format({True: '暂停', False: '运行'}[status[0]]))
        running_tasks.pop(task_id)
        print('任务完成，移出执行队列，id:{}'.format(task_id))


def kill_running_task(r_task_id):
    rt_lock.acquire()
    exists = False
    if r_task_id in waiting_order:
        exists = True
        waiting_order.remove(r_task_id)
    if r_task_id in waiting_tasks.keys():
        exists = True
        _ = waiting_tasks.pop(r_task_id)
        print('任务取消，id:{}'.format(r_task_id))
    if r_task_id in running_tasks.keys():
        exists = True
        r_task = running_tasks.pop(r_task_id)
        running_thread = r_task[-1]
        kill_thread(running_thread)
        print('任务终止，id:{}'.format(r_task_id))
    if r_task_id in suspend_handle.keys():
        exists = True
        status = suspend_handle.pop(r_task_id)
        print('任务终止前状态:{}，id:{}'.format({True: '暂停', False: '运行'}[status[0]], r_task_id))
    if r_task_id in finished_tasks:
        exists = True
        finished_tasks.remove(r_task_id)
        print('任务终止于任务完成后，id:{}'.format(r_task_id))
    if not exists:
        print('找不到对应的任务，id:{}'.format(r_task_id))
    rt_lock.release()
    return exists


def suspend_or_resume(task_id, suspend):
    if task_id in suspend_handle.keys():
        status = suspend_handle[task_id]
        status[0] = suspend
        return True
    else:
        return False


if __name__ == '__main__':
    def keep_generate_task():
        while True:
            task_ = [
                str(uuid.uuid4()),
                'task_hook.py',
                'task_map.pos',
                list(
                    set(
                        [
                            random.choice(
                                singleton_modules + [
                                    'ANDROID', 'AWVS', 'CONSOLE', 'DATABASE', 'EXCEL', 'HTTP', 'EWEB', 'MACC', 'LOG',
                                    'MISC', 'NESSUS', 'NMAP', 'RGSCAN', 'RSAS', 'ROTATE_PLATFORM', 'ROTATE_SHELF',
                                    'WEB_UI'
                                ]
                            ) for _ in range(random.randint(1, 10))
                        ]
                    )
                )
            ]
            create_waiting_task(task=task_)
            time.sleep(1)


    kgt_thread = threading.Thread(target=keep_generate_task)
    kgt_thread.start()
    while True:
        r_task_id_ = input()
        kill_running_task(r_task_id=r_task_id_)
