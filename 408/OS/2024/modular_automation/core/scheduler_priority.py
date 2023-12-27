import threading
import time

from kill_thread import kill_thread

from core.flow_chart import suspend_handle, run_flow_chart, finished_tasks, singleton_modules

ready_queue = []
ready_thread = {}
cpu_lock = threading.Lock()
cpu: dict[str, None | threading.Thread | list] = {'task': None, 'thread': None}


def api_create_waiting_task(task):
    task_id = task[0]
    ready_queue.append(task)
    print('任务送入等待队列，id:{}'.format(task_id))


def api_kill_running_task(r_task_id):
    exists = False
    if r_task_id in [task[0] for task in ready_queue]:
        exists = True
        pop_waiting_by_task_id(task_id=r_task_id)
    if r_task_id in ready_thread.keys():
        exists = True
        waiting_thread = ready_thread.pop(r_task_id)
        kill_thread(waiting_thread)
        print('任务取消，id:{}'.format(r_task_id))
    if r_task_id == cpu['task'][0]:
        exists = True
        cpu['task'] = None
        running_thread = cpu['thread']
        kill_thread(running_thread)
        print('任务终止，id:{}'.format(r_task_id))
    if r_task_id in suspend_handle.keys():
        exists = True
        status = suspend_handle.pop(r_task_id)
        print('任务终止前状态:{}，id:{}'.format({True: '暂停', False: '运行'}[status[0]], r_task_id))
    if r_task_id in finished_tasks:
        exists = True
        std_remove_finished_task(task_id_r=r_task_id)
        print('任务终止于任务完成后，id:{}'.format(r_task_id))
    if not exists:
        print('找不到对应的任务，id:{}'.format(r_task_id))
    return exists


def api_process_queued_task():
    while True:
        exclude = []
        cpu_lock.acquire()
        runnable = False
        from_ready = False
        cpu2ready = False
        task_id = ''
        while not runnable:
            task_id, priority = std_check_waiting_task(exclude=exclude)
            if task_id == '':
                print('无可执行等待任务')
                from_ready = False
                cpu2ready = False
                runnable = True
            else:
                if cpu['task'] is None and cpu['thread'] is None:
                    print('空闲让进')
                    from_ready = True
                    cpu2ready = False
                else:
                    task_r = cpu['task']
                    task_id_r, priority_r = task_r[0], task_r[-1]['priority']
                    if task_id_r in finished_tasks:
                        print('完成退出')
                        std_remove_finished_task(task_id_r=task_id_r)
                        from_ready = True
                        cpu2ready = False
                    else:
                        if priority_r < priority:
                            print('高优抢占')
                            from_ready = True
                            cpu2ready = True
                        else:
                            print('低优等待')
                            from_ready = False
                            cpu2ready = False
                runnable = std_check_conflict_task(task_id=task_id)
                if not runnable:
                    exclude.append(task_id)
        if cpu2ready:
            print('挂起→就绪')
            pause_running_task()
        if from_ready:
            print('就绪→执行')
            std_execute_runnable_task(task_id=task_id)
        cpu_lock.release()
        time.sleep(0.25)


def api_suspend_or_resume(task_id, suspend):
    cpu_lock.acquire()
    task_r = cpu['task']
    task_id_r = task_r[0]
    if task_id_r != task_id:
        if suspend:
            print('要求挂起，实际也挂起（未运行）')
            exist = False
        else:
            print('要求运行，实际挂起（未运行），强制执行（无视模块资源冲突）')
            pause_running_task()
            std_execute_runnable_task(task_id=task_id)
            exist = True
    else:
        if suspend:
            print('要求挂起，实际运行')
            exclude = []
            runnable = False
            while not runnable:
                task_id, priority = std_check_waiting_task(exclude=exclude)
                if task_id == '':
                    print('无可执行等待任务')
                    runnable = True
                else:
                    runnable = std_check_conflict_task(task_id=task_id)
                    if not runnable:
                        exclude.append(task_id)
            pause_running_task()
            if task_id != '':
                std_execute_runnable_task(task_id=task_id)
            exist = True
        else:
            print('要求运行，实际运行')
            exist = False
    cpu_lock.release()
    return exist


def pop_waiting_by_task_id(task_id):
    remove_index = None
    for i in range(len(ready_queue)):
        task = ready_queue[i]
        if task_id == task[0]:
            remove_index = i
            break
    if remove_index is not None:
        return ready_queue.pop(remove_index)
    else:
        return None


def pause_running_task():
    task = cpu['task']
    task_id = task[0]
    ready_queue.append(task)
    ready_thread[task_id] = cpu['thread']
    suspend_handle[task_id][0] = True
    cpu['task'] = None
    cpu['thread'] = None


def std_check_conflict_task(task_id):
    task_c = None
    for i in range(len(ready_queue)):
        task = ready_queue[i]
        if task_id == task[0]:
            task_c = task
            break
    task = task_c
    if task is None:
        return False
    runnable = True
    involved_modules = task[3]
    for r_task in ready_queue:
        r_involved_modules = r_task[3]
        common_modules = list(set(involved_modules).intersection(set(r_involved_modules)))
        for m in common_modules:
            if m in singleton_modules:
                print('任务:{}与并发任务:{}存在资源冲突，冲突模块为:{}'.format(task[0], r_task[0], m))
                runnable = False
                break
    return runnable


def std_check_waiting_task(exclude):
    # find_highest_waiting
    priority_ = 0
    task_id_ = ''
    for task in ready_queue:
        task_id = task[0]
        if task_id not in exclude:
            prerequisite = task[-1]
            priority = prerequisite['priority']
            if priority > priority_:
                priority_ = priority
                task_id_ = task_id
    return task_id_, priority_


def std_execute_runnable_task(task_id):
    task = pop_waiting_by_task_id(task_id)
    cpu['task'] = task
    task_id = task[0]
    if task_id in ready_thread.keys():
        print('恢复暂停')
        cpu['thread'] = ready_thread.pop(task_id)
        suspend_handle[task_id][0] = False
    else:
        print('从头开始')
        cpu['thread'] = threading.Thread(target=run_flow_chart, args=tuple(task))
        cpu['thread'].start()


def std_remove_finished_task(task_id_r):
    finished_tasks.remove(task_id_r)
    if cpu['task'][0] == task_id_r:
        kill_thread(cpu['thread'])
        cpu['task'] = None
        cpu['thread'] = None
# todo: pending test
