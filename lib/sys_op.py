# Config operations
import esp, esp32
import hw
from op import Operator, result, GET, SET
from utils import singleton, random_string
from uasyncio import sleep, create_task
from os import uname
from sys import version
from machine import reset, freq
from config_op import ConfigOp
from utime import time

LABEL = "label"
SECRET = "secret"
NTPHOST = "ntphost"
CONFIG_FILE = "/dat/config.json"

@singleton
class SysOp(ConfigOp):
    def __init__(self, opc):
        self.__opc = opc
        self.__config = None
        ConfigOp.__init__(self, 'sys', CONFIG_FILE)
        self.commands.pop('sys/config:set') # 取消设置功能
        self.add_command(self.__info, GET, 'info')
        self.add_command(self.__commands, GET, 'commands')
        self.add_command(self.__echo, SET, 'echo')
        self.add_command(self.__reboot, SET, 'reboot')

    @property
    def ntphost(self):
        if self.__config != None and NTPHOST in self.__config:
            return self.__config[NTPHOST]
        return hw.NTP_HOST

    @property
    def device_secret(self):
        return self.__config[SECRET]

    @property
    def device_lable(self):
        return self.__config[LABEL]

    def __init_defaults(self, force = False):
        changes = 0
        if self.__config == None:
            self.__config = {}
        if SECRET not in self.__config or force:
            self.__config[SECRET] = random_string(32)
            changes += 1
        if LABEL not in self.__config or force:
            self.__config[LABEL] = self.device_name
            changes += 1
        return changes

    def init_config(self, force = False):
        if self.__init_defaults(force) > 0:
            self.__save()

    async def __reboot(self, _):
        create_task(self.__delay_reboot())
        return result(200, m = '', v = {"message": "Reboot after 5 seconds"})

    async def __delay_reboot(self):
        await sleep(5)
        reset()

    async def __info(self, _):
        v = {}
        v['sys-version'] = version
        v['uname'] = uname()
        v['frequence'] = freq()
        v['unique-id'] = hw.UNIQUE_ID
        v['flash-size'] = esp.flash_size()
        v['flash-user-start'] = esp.flash_user_start()
        v['hall-sensor'] = esp32.hall_sensor()
        v['raw-temperature'] = esp32.raw_temperature()
        v['type'] = hw.TYPE
        v['wifi'] = hw.WIFI
        v['wifi-check-interval'] = hw.WIFI_CHECK_INTVAL
        v['wifi-check-type'] = hw.WIFI_CHECK_TYPE
        v['wifi-check-host'] = hw.WIFI_CHECK_HOST
        v['blu-uart'] = hw.BLE_UART
        v['mqtt'] = hw.MQTT
        v['http'] = hw.HTTP
        v['ntp'] = hw.NTP
        v['device-name'] = hw.DEVICE_NAME
        v['mac-address'] = hw.MAC
        v['ntp-host'] = hw.NTP_HOST
        v['ntp-interval'] = hw.NTP_INTERVAL
        v['time'] = time()
        await sleep(0)
        return result(200, None, v)

    async def __commands(self, _):
        v = []
        for i in self.__opc.commands:
            v.append(i)
        await sleep(0)
        return result(200, None, v)

    async def __echo(self, param):
        hw.log.info(param)
        await sleep(0)
        return result(200, None, param)
