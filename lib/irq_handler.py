# Abstract IRQ safe handler
from machine import Pin, disable_irq, enable_irq
from micropython import schedule
from uasyncio import create_task
from hw import log

class IrqProducer:
    def __init__(self, trigger = Pin.IRQ_RISING):
        self.handler = None
        self.__handler_data = None
        self.queue = None
        self.trigger = trigger
        self.__irq = None

    def _get_data(self, b): #NOSONAR
        pass

    def __callback(self, b):
        log.debug("IRQ data: %r", b)
        state = disable_irq()
        try:
            self._get_data(b)
            if self.handler is not None:
                schedule(self.handler, self.__handler_data)
            if self.queue is not None:
                create_task(self.queue.put(self.__handler_data))
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
