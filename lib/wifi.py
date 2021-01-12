# Wifi connection class
from time import time
from network import WLAN, STA_IF
from utils import singleton, is_str_empty, delayed_task
from relay import Relay
from uping import ping_check
from config_op import ConfigOp
from micropython import const
from uasyncio import sleep, sleep_ms
from op import GET, SET, result
from hw import log, MAC
import hw

SSID = "ssid"
TIMEOUT = "timeout"
PASSWORD = "password"
YBBHOME = "ybbhome"
WIFI_CHECK_HOST = 'wifi_check_host'
RECONNECT_WIFI = 'Reconnect Wifi after 5 seconds.'
CONFIG_NAME = "/dat/wifi.json" # Config file
DEFAULT_TMOUT = const(15)
DEFAULT_300 = const(300)

@singleton
class Wifi(ConfigOp):
    def __init__(self, hostname, pin = 2):
        self.__wlan = None
        self.__timeout = DEFAULT_TMOUT
        self.__led = Relay(pin)
        self.is_ok = False
        self.gw = None
        self.ip = None
        self.dns = None
        ConfigOp.__init__(self, 'wifi', CONFIG_NAME)
        self.add_command(self.__get_info, GET)
        self.add_command(self.__reconnect, SET, 'reconnect')
        self.__hostname = hostname

    def is_connected(self):
        return self.__wlan != None and self.__wlan.isconnected()

    async def __get_info(self, _):
        v = self.get_info()
        await sleep(0)
        return result(200, None, v)

    async def __reconnect(self, _):
        delayed_task(5000, self.async_connect, (True), True)
        return result(200, None, RECONNECT_WIFI)

    async def __reload_config(self): # NOSONAR
        return await self.__reconnect(None)

    def get_info(self):
        return {
            "mac": MAC,
            "connected": self.is_connected(),
            "connection tested": self.is_ok,
            "hostname": self.__hostname,
            "ip": self.ip,
            "gw": self.gw,
            "dns": self.dns
        }

    def check_wifi_config(self):
        self.load()
        return not (self.__config is None or is_str_empty(self.__config[SSID]) or is_str_empty(self.__config[PASSWORD]))

    def disconnect(self):
        if self.__wlan is not None and self.__wlan.isconnected():
            self.__wlan.disconnect()
            self.__wlan.active(False)

    async def async_connect(self, force_rec = False):
        if self.__wlan is not None and self.__wlan.isconnected():
            if force_rec:
                self.disconnect()
                return await self.__async_connect()
            return True
        return await self.__async_connect()

    async def __async_connect(self):
        self.__connect_init()
        return await self.__async_connect_finish()

    async def __async_connect_finish(self):
        start_time = time() # Check time
        while not self.__wlan.isconnected():
            await sleep_ms(DEFAULT_300)
            self.__led.on()
            await sleep_ms(DEFAULT_300)
            self.__led.off()
            if time()-start_time > self.__timeout:
                log.error("Wifi connection timeout: %d", self.__timeout)
                break
        return self.__set_properties()

    def __connect_init(self):
        self.check_wifi_config()
        if self.__config is None:
            log.error("Wifi config is None")
            return
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
            (self.ip, _, self.gw, self.dns) = self.__wlan.ifconfig()
            self.is_ok = True
            self.__led.on()
        else:
            self.ip = None
            self.gw = None
            self.dns = None
            self.is_ok = False
            self.__wlan = None
            self.__led.off()
        return self.is_ok

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
        log.debug("Setup wifi monitor")
        while hw.WIFI:
            try:
                await sleep(hw.WIFI_CHECK_INTVAL)
                if not self.check_connection():
                    log.info("Wifi is not ready, reconnecting...")
                    await self.async_connect(True)
            except: #NOSONAR # pylint: disable=W0702
                pass
