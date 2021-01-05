# Touch button
# 按钮一端接地，一端接 ADC Touch，比如32

from machine import Pin
import time
from button import Button

def demo():
    LED=Pin(2,Pin.OUT) #构建LED对象,开始熄灭
    state = 0
    b = Button(32)
    '''
    # 直接测试按钮
    while True:
        if b.is_on(): #  默认 10ms 抖动消除
            state = not state
            LED.value(state)
            while b.is_not_off(): # 监测按键是否复位，默认不需要抖动消除
                pass
    '''
    # IRQ方式
    def show(args):
        print("pressed ", args)

    b.set_handler(show)
    time.sleep(5)
    b.remove_handler()

if __name__ == "__main__":
    demo()
