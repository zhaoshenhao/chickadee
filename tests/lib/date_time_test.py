from date_time import *

def demo():
    print(time_stamp())
    print(today(FMT_YMD))
    print(today(FMT_YMD_C))
    print(today(FMT_YMD_U))
    print(time(FMT_HMS))
    print(time(FMT_HMS_C))
    print(time(FMT_HMS_U))
    print(now(FMT_YMDHMS))
    print(now(FMT_YMDHMS_C))
    print(now(FMT_YMDHMS_U))
    print(now_with_ms(FMT_YMDHMSS))
    print(now_with_ms(FMT_YMDHMSS_C))
    print(now_with_ms(FMT_YMDHMSS_U))

if __name__ == "__main__":
    demo()
