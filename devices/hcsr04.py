from machine import Pin
from sensor import Producer
from utime import sleep_us,ticks_us

# 超声波距离测量传感器

class HCSR04(Producer):
    def __init__(self, trig_pin = 17, echo_pin = 16, name = 'hcsr04'):
        #初始化接口 trig=17,echo=16
        self.trig = Pin(trig_pin,Pin.OUT)
        self.echo = Pin(echo_pin,Pin.IN)
        Producer.__init__(self, name, 1000, 100)
        self.add_sensor("distance", self.get_distance)

    def get_distance(self):
        distance=0
        self.trig.value(1)
        sleep_us(20)
        self.trig.value(0)
        while self.echo.value() == 0:
            pass
        if self.echo.value() == 1:
            ts=ticks_us()                   #开始时间
            while self.echo.value() == 1:   #等待脉冲高电平结束
                pass
            te=ticks_us()                   #结束时间
            tc=te-ts                        #回响时间（单位us，1us=1*10^(-6)s）
            distance=(tc*170)/10000         #距离计算 （单位为:cm）
        return distance