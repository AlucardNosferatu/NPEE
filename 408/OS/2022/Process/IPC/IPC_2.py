import time
from multiprocessing import shared_memory, Queue


def ipc_sm():
    shm = shared_memory.SharedMemory(name='shm_20291224')
    content = shm.buf.tobytes()
    print(content)


def ipc_q_p2(q_inst: Queue):
    while True:
        time.sleep(1)
        res = q_inst.get()
        print(res)


if __name__ == "__main__":
    q = Queue()
    ipc_q_p2(q)
