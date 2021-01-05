# Abstract IRQ safe handler
import micropython
import machine
from hw import log

class IrqHandler:
    def __init__(self):
        self._handler = None
        self._handler_data = None
        self._trigger = None
    
    def _check_irq(self, b):
        return True

    def _callback(self, b):
        if self._handler == None:
            return
        state = machine.disable_irq()
        try:
            if self._check_irq(b):
                micropython.schedule(self._handler, self._handler_data)
        except Exception as e:
            log.error("Excetion while check and call irq handler")
        machine.enable_irq(state)

    def _set_handler(self, fun, trigger): # Let child override and call this
        self._handler = fun
        self._trigger = trigger

    def _remove_handler(self): # Let child override and call this
        self._handler = None
