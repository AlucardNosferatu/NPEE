import time
import uuid
from multiprocessing import shared_memory, Pipe, Process


def ipc_sm():
    shm = shared_memory.SharedMemory(name='shm_20291224', create=True, size=4097)
    shm.buf[:4] = bytearray([20, 29, 12, 24])
    input()
    shm.close()
    print('Done')


def ipc_pipe():
    (con1, con2) = Pipe(duplex=True)
    pro1 = Process(target=ipc_pipe_p1, name='p1', args=(con1,))
    pro2 = Process(target=ipc_pipe_p2, name='p2', args=(con2,))
    pro1.start()
    pro2.start()
    input()
    pro1.kill()
    pro2.kill()


def ipc_pipe_p1(pipe):
    while True:
        time.sleep(1)
        pipe.send(['p1', str(uuid.uuid4())])
        time.sleep(1)
        print(pipe.recv())


def ipc_pipe_p2(pipe):
    time.sleep(0.5)
    while True:
        time.sleep(1)
        print(pipe.recv())
        time.sleep(1)
        pipe.send(['p2', str(uuid.uuid4())])


if __name__ == "__main__":
    ipc_pipe()
