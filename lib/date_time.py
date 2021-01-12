# 一些常用的日期时间函数

import machine
import utime

FMT_YMD = '{:02d}{:02d}{:02d}'
FMT_YMD_C = '{:02d}-{:02d}-{:02d}'
FMT_YMD_U = '{:02d}_{:02d}_{:02d}'
FMT_HMS = '{:02d}{:02d}{:02d}'
FMT_HMS_C = '{:02d}:{:02d}:{:02d}'
FMT_HMS_U = '{:02d}_{:02d}_{:02d}'
FMT_YMDHMS = '{:02d}{:02d}{:02d}{:02d}{:02d}{:02d}'
FMT_YMDHMS_C = '{:02d}-{:02d}-{:02d} {:02d}{:02d}{:02d}'
FMT_YMDHMS_U = '{:02d}_{:02d}_{:02d}_{:02d}_{:02d}_{:02d}'
FMT_YMDHMSS = '{:02d}{:02d}{:02d}{:02d}{:02d}{:02d}{:03d}'
FMT_YMDHMSS_C = '{:02d}:{:02d}:{:02d} {:02d}:{:02d}:{:02d}.{:03d}'
FMT_YMDHMSS_U = '{:02d}_{:02d}_{:02d}_{:02d}_{:02d}_{:02d}_{:03d}'

def get_time():
    return machine.RTC().datetime()

def time_stamp():
    return 946684800 + utime.time()

def time(fmt):
    (_, _, _, _, h, mins, s, _) = get_time()
    return fmt.format(h, mins, s)

def today(fmt):
    (y, m, d, _, _, _, _, _) = get_time()
    return fmt.format(y, m, d)

def now(fmt):
    (y, m, d, _, h, mins, s, _) = get_time()
    return fmt.format(y, m, d, h, mins, s)

def now_with_ms(fmt):
    (y, m, d, _, h, mins, s, ss) = get_time()
    ms = int(ss / 1000)
    return fmt.format(y, m, d, h, mins, s, ms)

