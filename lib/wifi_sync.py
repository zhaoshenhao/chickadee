from time import time, sleep_ms #pylint: disable=no-name-in-module
from wifi import Wifi, DEFAULT_300
from hw import log

class WifiSync(Wifi):
    def __init__(self, hostname, pin = 2):
        Wifi.__init__(self, hostname, pin)

    def connect(self, force_rec = False):
        if self.__wlan is not None and self.__wlan.isconnected():
            if not force_rec:
                return True
            self.disconnect()
            return self.__connect()
        return self.__connect()

    def __connect(self):
        self.__connect_init()
        return self.__connect_finish()

    def __connect_finish(self):
        start_time = time() # Check time
        while not self.__wlan.isconnected():
            sleep_ms(DEFAULT_300)
            self.__led.on()
            sleep_ms(DEFAULT_300)
            self.__led.off()
            if time()-start_time > self.__timeout:
                log.error("Wifi connection timeout: %d", self.__timeout)
                break
        return self.__set_properties()

