import os
import random
import time


if __name__ == '__main__':
    delay_base = random.randint(110, 1000)
    while True:
        cd = random.choice([random.randint(1, 6), random.randint(1, 12), random.randint(1, 25)])
        delay_offset = random.randint(-100, 100)
        while cd > 0:
            delay = delay_base+delay_offset
            delay_str = '   {}ms   '.format(delay)
            os.system('cls')
            print(delay_str, cd)
            cd -= 1
            time.sleep(0.025)
        delay_base = delay
