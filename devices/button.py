# Touch button
# 按钮一端接地，一端接 ADC Touch，比如32

from machine import Pin
from irq_handler import IrqHandler
import time
from micropython import const

ON = const(0)
OFF = not ON

class Button(IrqHandler):
    def __init__(self, pin):
        IrqHandler.__init__(self)
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
                time.sleep_ms(duration)
            else:
                return True
            return self.get_value() == status
        return False

    def get_value(self):
        return self._button.value()

    def _check_irq(self, b):
        if self._duration > 0:
            time.sleep_ms(self._duration)
            if self._trigger == Pin.IRQ_FALLING or self._trigger == Pin.IRQ_LOW_LEVEL:
                if self.get_value() == ON:
                    return True
            else:
                if self.get_value() == OFF:
                    return True
        else:
            return True
        return False
    
    # triggere: Pin.IRQ_FALLING, Pin.IRQ_RISING, Pin.IRQ_LOW_LEVEL, Pin.IRQ_HIGH_LEVEL
    def set_handler(self, fun, duration = 10, trigger = Pin.IRQ_FALLING):
        self._set_handler(fun, trigger)
        self._duration = duration
        self._button.irq(self._callback, self._trigger)

    def remove_handler(self):
        self._remove_handler()
        self._button.irq(None, self._trigger)

