# PIR sensor (人体移动感应）
# 这个传感器自带监测冷却器，所以不需要去除监测抖动
from utils import time_stamp
from irq_producer import IrqProducer
from machine import Pin

class Pir(IrqProducer):
    def __init__(self, pin, name = 'pir'):
        IrqProducer.__init__(self, name)
        self.__irq = Pin(pin, Pin.IN, Pin.PULL_UP) #NOSONAR

    def _get_data(self, b):
        self.__handler_data = { #NOSONAR
            'd': self.name,
            'tm': time_stamp(),
            's': [{
                'n': 'alert',
                'v': 1
            }]
        }
