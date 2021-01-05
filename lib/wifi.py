# Wifi connection class
import hw
from ustruct import unpack
from time import time, sleep_ms
from network import WLAN, STA_IF
from utils import singleton, is_str_empty
from relay import Relay
from uping import ping_check
from config_op import ConfigOp
from micropython import const
from hw import log, MAC
from uasyncio import sleep
from op import GET, SET, result

SSID = "ssid"
TIMEOUT = "timeout"
PASSWORD = "password"
YBBHOME = "ybbhome"
WIFI_CHECK_HOST = 'wifi_check_host'
CONFIG_NAME = "/dat/wifi.json" # Config file
DEFAULT_TMOUT = const(15)
DEFAULT_300 = const(300)

@singleton
class Wifi(ConfigOp):
    def __init__(self, hostname = None, pin = 2):
        self.__wlan = None
        self.__timeout = DEFAULT_TMOUT
        self.__led = Relay(pin)
        self.__is_ok = False
        self.__gw = None
        self.__ip = None
        self.__dns = None
        ConfigOp.__init__(self, 'wifi', CONFIG_NAME)
        self.add_command(self.__get_info, GET)
        self.add_command(self.__reconnect, SET, 'reconnect')

        if hostname != None:
            self.__hostname = hostname
        else:
            self.__hostname = YBBHOME

    def config(self):
        return self.__config

    def is_connected(self):
        return self.__wlan != None and self.__wlan.isconnected()

    def gw(self):
        return self.__gw

    def ip(self):
        return self.__ip

    def is_ok(self):
        return self.__is_ok

    def dns(self):
        return self.__dns

    async def __get_info(self, _):
        v = self.get_info()
        await sleep(0)
        return result(200, None, v)

    async def __reconnect(self, _):
        from micropython import schedule
        schedule(self.connect(True))
        return result()

    def get_info(self):
        return {
            "mac": MAC,
            "connected": self.is_connected(),
            "connection tested": self.__is_ok,
            "hostname": self.__hostname,
            "ip": self.__ip,
            "gw": self.__gw,
            "dns": self.__dns
        }

    def check_wifi_config(self):
        self.__config = self.load()
        return not (self.__config == None or is_str_empty(self.__config[SSID]) or is_str_empty(self.__config[PASSWORD]))

    def disconnect(self):
        if self.__wlan != None and self.__wlan.isconnected():
            self.__wlan.disconnect()
            self.__wlan.active(False)

    '''
    异步连接系列函数
    '''
    async def async_connect(self, force_rec = False):
        if self.__wlan != None and self.__wlan.isconnected():
            if not force_rec:
                return True
            else:
                self.disconnect()
                return await self.__async_connect()
        return await self.__async_connect()

    async def __async_connect(self):
        self.__connect_init()
        return await self.__async_connect_finish()

    async def __async_connect_finish(self):
        from uasyncio import sleep_ms as asleep_ms
        start_time = time() # Check time
        while not self.__wlan.isconnected():
            await asleep_ms(DEFAULT_300)
            self.__led.on()
            await asleep_ms(DEFAULT_300)
            self.__led.off()
            if time()-start_time > self.__timeout:
                log.error("Wifi connection timeout: %d", self.__timeout)
                break
        return self.__set_properties()

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

    def __connect_init(self):
        self.check_wifi_config()
        if self.__config == None:
            log.error("Wifi config is None")
            return False
        log.info("Connect to wifi: %s", self.__config[SSID])
        self.__wlan = WLAN(STA_IF)  # 创建 station 接口
        if self.__wlan.isconnected():
            self.__wlan.disconnect()
        self.__wlan.active(True)  # Activate the interface
        self.__wlan.scan()  # Scan
        self.__led.off()
        self.__wlan.config(dhcp_hostname = self.__hostname)
        self.__wlan.connect(self.__config[SSID], self.__config[PASSWORD])  # 连接到指定ESSID网络
        if TIMEOUT in self.__config:
            self.__timeout = self.__config[TIMEOUT]

    def __set_properties(self):
        if self.__wlan.isconnected():
            log.info('network information: %s', str(self.__wlan.ifconfig()))
            (self.__ip, _, self.__gw, self.__dns) = self.__wlan.ifconfig()
            self.__is_ok = True
            self.__led.on()
            return True
        else:
            self.__ip = None
            self.__gw = None
            self.__dns = None
            self.__is_ok = False
            self.__wlan = None
            self.__len.off
            return False

    def check_connection(self):
        if hw.WIFI_CHECK_TYPE == 0:
            return True
        if not self.is_connected():
            return False
        if hw.WIFI_CHECK_TYPE == 1:
            return True
        dest = self.gw
        if hw.WIFI_CHECK_TYPE == 3:
            if WIFI_CHECK_HOST in self.__config != None:
                dest = self.__config[WIFI_CHECK_HOST]
            else:
                dest = hw.WIFI_CHECK_HOST
        return ping_check(dest)

    async def monitor(self):
        from uasyncio import sleep as asleep
        log.debug("Setup wifi monitor")
        while hw.WIFI:
            try:
                log.debug("Check wifi ...")
                s = DEFAULT_300 # 设置一个默认值
                if hw.WIFI_CHECK_TYPE != 0 and hw.WIFI_CHECK_INTVAL > 0 and hw.WIFI_CHECK_INTVAL < DEFAULT_300:
                    s = hw.WIFI_CHECK_INTVAL
                await asleep(s)
                if not self.check_connection():
                    log.info("Wifi is not ready, reconnecting...")
                    await self.async_connect(True)
            except: #NOSONAR
                pass
