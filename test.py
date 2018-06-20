import time
t = 0.1
a = 1
v = 1
a1 = 10

for i in range(1000):
    if i > 5:
        print(v)
        v += 10
    else:
        print(v)
        v += 1
    time.sleep(t)
    t -= 0.0001

