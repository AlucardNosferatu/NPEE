from multiprocessing import shared_memory


def ipc_sm():
    shm = shared_memory.SharedMemory(name='shm_20291224', create=True, size=4097)
    shm.buf[:4] = bytearray([20, 29, 12, 24])
    input()
    shm.close()
    print('Done')


if __name__ == "__main__":
    ipc_sm()
