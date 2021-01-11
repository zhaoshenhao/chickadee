from wifi import Wifi, DEFAULT_300
from hw import log

'''
为减少代码内存消耗，特把同步连接分离在次。本类只用在测试中。
'''
class WifiSync(Wifi):
    def __init__(self, hostname, pin = 2):
        Wifi.__init__(self, hostname, pin)

    '''
    同步连接系列函数
    '''
    def connect(self, force_rec = False):
        if self.__wlan != None and self.__wlan.isconnected():
            if not force_rec:
                return True
            else:
                self.disconnect()
                return self.__connect()
        return self.__connect()

    def __connect(self):
        self.__connect_init()
        return self.__connect_finish()

    def __connect_finish(self):
        from time import time, sleep_ms
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

