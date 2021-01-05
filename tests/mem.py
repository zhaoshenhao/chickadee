from gc import collect, threshold, mem_alloc
from micropython import mem_info
mem_info()
collect()
threshold(gc.mem_free() // 4 + mem_alloc())
mem_info()