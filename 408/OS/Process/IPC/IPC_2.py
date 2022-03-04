from multiprocessing import shared_memory


def ipc_sm():
    shm = shared_memory.SharedMemory(name='shm_20291224')
    content = shm.buf.tobytes()
    print(content)


if __name__ == "__main__":
    ipc_sm()
