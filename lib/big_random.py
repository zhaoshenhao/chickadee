import os

def count_bytes(i):
    l = 128
    bs = i.to_bytes(l, 'big')
    cnt = 0
    for b in bs:
        if b == 0:
            cnt += 1
        else:
            return l - cnt
    return 0

def random_bigint(bound):
    bl = count_bytes(bound) - 1
    bs = os.urandom(bl)
    return int.from_bytes(bs, 'big')

