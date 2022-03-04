import psutil

this_process = psutil.Process()
with open('pid', mode='w') as f:
    f.write(str(this_process.pid))

while True:
    a = 1224
