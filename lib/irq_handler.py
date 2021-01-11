# Abstract IRQ safe handler
from hw import log
from machine import Pin

class IrqHandler:
    def __init__(self, trigger = Pin.IRQ_RISING):
        self.handler = None
        self.__handler_data = None
        self.queue = None
        self.trigger = trigger
        self.__irq = None
    
    def _get_data(self, b): #NOSONAR
        pass

    def __callback(self, b):
        from micropython import schedule
        from machine import disable_irq, enable_irq
        log.debug("IRQ data: %r" % b)
        state = disable_irq()
        try:
            self._get_data(b)
            if self.handler is not None:
                schedule(self.handler, self.__handler_data)
            if self.queue is not None:
                from uasyncio import create_task
                create_task(self.queue.put(self.__handler_data))
        except Exception as e:
            log.error("Excetion while check and call irq handler: %r" % e)
        enable_irq(state)

    def setup(self, queue):
        self.queue = queue
        self.enable()

    def enable(self):
        self.__irq.irq(self.__callback, self.trigger)

    def disable(self):
        self.__irq.irq(None, self.trigger)
