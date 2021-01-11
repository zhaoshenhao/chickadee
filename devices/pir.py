# PIR sensor (人体移动感应）
# 这个传感器自带监测冷却器，所以不需要去除监测抖动

from irq_handler import IrqHandler
from machine import Pin

class Pir(IrqHandler):
    def __init__(self, pin):
        IrqHandler.__init__(self)
        self.__irq = Pin(pin, Pin.IN, Pin.PULL_UP) #NOSONAR

    def _get_data(self, b):
        self.__handler_data = { #NOSONAR
            'd': 'pir',
            's': [{
                'n': 'alert',
                'v': 1
            }]
        }
