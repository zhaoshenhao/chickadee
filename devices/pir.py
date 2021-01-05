# PIR sensor (人体移动感应）
# 这个传感器自带监测冷却器，所以不需要去除监测抖动

from sensor import IrqProducer
from machine import Pin

class Pir(IrqHandler):
    def __init__(self, pin):
        IrqHandler.__init__(self)
        self._pin = pin
        self._pir = Pin(self._pin, Pin.IN, Pin.PULL_UP)

    def set_handler(self, fun, trigger = Pin.IRQ_RISING):
        self._set_handler(fun, trigger)
        self._pir.irq(self._callback, self._trigger)

    def remove_handler(self):
        self._remove_handler()
        self._pir.irq(None, self._trigger)

