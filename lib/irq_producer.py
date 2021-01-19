# Abstract IRQ safe handler
from utime import ticks_ms
from machine import Pin, disable_irq, enable_irq
from micropython import schedule
from uasyncio import create_task, sleep_ms
from hw import log

class IrqProducer:
    def __init__(self, name, trigger = Pin.IRQ_RISING):
        self.handler = None
        self.__handler_data = None
        self.queue = None
        self.trigger = trigger
        self.__irq = None
        self.name = name
        self.ticks = ticks_ms()
        self.cool_down_gap = 0    # ms. During this time, device will neglect any IRQ
        self.interval = 0 # ms. Device will sleep before next check 

    def _get_data(self, b): #NOSONAR
        pass

    def __callback(self, b):
        log.debug("IRQ data: %r", b)
        state = disable_irq()
        tm = ticks_ms()
        log.debug("tm: %d, old: %d, %gap", tm, self.ticks, self.cool_down_gap)
        if tm > self.ticks + self.cool_down_gap:
            self.ticks = tm
            try:
                self._get_data(b)
                if self.handler is not None:
                    log.debug("Call handler")
                    schedule(self.handler, self.__handler_data)
                if self.queue is not None:
                    log.debug("Send sensor data to queue")
                    create_task(self.queue.put(self.__handler_data))
                sleep_ms(self.interval)
            except BaseException as e: # NOSONAR
                log.error("Excetion while check and call irq handler: %r", e)
        enable_irq(state)

    def setup(self, queue):
        self.queue = queue
        self.enable()

    def enable(self):
        self.__irq.irq(self.__callback, self.trigger)

    def disable(self):
        self.__irq.irq(None, self.trigger)
