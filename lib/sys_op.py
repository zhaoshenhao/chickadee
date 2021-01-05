# Config operations
import esp, esp32
import hw
from op import Operator, result, GET, SET
from utils import singleton
from uasyncio import sleep, create_task
from os import uname
from sys import version
from machine import reset, freq

@singleton
class SysOp(Operator):
    def __init__(self, opc):
        Operator.__init__(self, "sys")
        self.add_command(self.__get, GET, 'info')
        self.add_command(self.__commands, GET, 'commands')
        self.add_command(self.__echo, SET, 'echo')
        self.add_command(self.__reboot, SET, 'reboot')
        self.__opc = opc

    async def __reboot(self, _):
        create_task(self.__delay_reboot())
        return result(200, m = '', v = {"message": "Reboot after 5 seconds"})

    async def __delay_reboot(self):
        await sleep(5)
        reset()

    async def __get(self, _):
        v = {}
        v['sys-version'] = version
        v['uname'] = uname
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
