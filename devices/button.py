# Touch button
# 按钮一端接地，一端接 ADC Touch，比如32

from time import time, sleep_ms #pylint: disable=no-name-in-module
from machine import Pin
from irq_producer import IrqProducer
from micropython import const

ON = const(0)
OFF = not ON

class Button(IrqProducer):
    def __init__(self, pin, name = 'button'):
        IrqProducer.__init__(self, name)
        self._pin = pin
        self._button = Pin(self._pin, Pin.IN, Pin.PULL_UP)

    def is_on(self, duration = 10):
        return self._is_status(ON, duration)

    def is_off(self, duration = 10):
        return self._is_status(OFF, duration)

    def is_not_on(self, duration = 0): # this is safer to detecte value is not 0 (on)
        return not self.is_on(duration)

    def is_not_off(self, duration = 0): # this is safer to detect value is not 1 (off)
        return not self.is_off(duration)

    def _is_status(self, status, duration = 10):
        if self.get_value() == status:
            if duration > 0:
                sleep_ms(duration)
            else:
                return True
            return self.get_value() == status
        return False

    def get_value(self):
        return self._button.value()

    def _get_data(self, _):
        self.__handler_data = {
            'd': self.name,
            'tm': time(),
            's': [{
                'n': 'alert',
                'v': 1
            }]
        }
