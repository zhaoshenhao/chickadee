# The device class contains all necessary generic device operation
from gc import collect
from time import time
from machine import Pin,freq, reset
from uasyncio import create_task, sleep, get_event_loop
from primitives.pushbutton import Pushbutton
from utils import singleton, set_gc
from micropython import const, mem_info
from relay import Relay
import hw
import dev

LOWER_POWER_FEQ = const(80000000)
SYS_STATE_NONE = const(0)
SYS_STATE_REBOOT = const(1)
SYS_STATE_CONFIG = const(2)
SYS_STATE_RESET = const(3)
SYS_STATE_TIMEOUT = const(30) # 系统状态超时，系统进入某种状态，比如重启，没有下一步操作，超时后返回常规状态

@singleton
class Board:
    def __init__(self):
        self.__led = Relay(hw.WIFI_LED_PIN)
        self.__in_error_mode = False
        self.__state_start = 0

    async def start(self):
        try:
            hw.log.info("Starting device...")
            set_gc()
            collect()
            await self.__setup_button()
            collect()
            await self.__setup_ble()
            collect()
            await self.__setup_wifi()
            collect()
            await self.__setup_http()
            collect()
            await self.__setup_mqtt()
            collect()
            await self.__setup_scheduler()
            collect()
            await self.__setup_devices()
            collect()
            hw.log.info("Device started.")
        except BaseException as e:
            hw.log.error("Start device failed! Exception: %s\nEntering error mode.", e)
            freq(LOWER_POWER_FEQ)
            self.__in_error_mode = True
            self.__setup_led()
            raise e
        get_event_loop().run_forever()

    def __setup_led(self):
        self.__led.stop_async_blink()
        hw.log.debug("State: %d, set led." % dev.state)
        if dev.state == SYS_STATE_REBOOT:
            create_task(self.__led.async_blink(300, 300))
        elif dev.state == SYS_STATE_CONFIG:
            create_task(self.__led.async_blink(200, 200))
        elif dev.state == SYS_STATE_RESET:
            create_task(self.__led.async_blink(100, 100))
        elif self.__in_error_mode:
            create_task(self.__led.async_blink(100, 5000))

    def __long_press(self):
        '''
        配置长按操作
        '''
        self.__state_start = time()
        if dev.state == SYS_STATE_NONE:
            dev.state = SYS_STATE_REBOOT
        elif dev.state == SYS_STATE_REBOOT:
            dev.state = SYS_STATE_CONFIG
        elif dev.state == SYS_STATE_CONFIG:
            dev.state = SYS_STATE_RESET
        else:
            dev.state = SYS_STATE_NONE
            self.__state_start = 0
        self.__setup_led()

    def __double_press(self):
        '''
        配置短按操作
        '''
        if dev.state == SYS_STATE_REBOOT:
            hw.log.info("Reboot from button")
            reset()
        elif dev.state == SYS_STATE_CONFIG:
            from wifi_ap import WifiAp
            ap = WifiAp()
            ap.start_ap()
            hw.log.info("Ap network: %r", ap.get_info())
        elif dev.state == SYS_STATE_RESET:
            hw.log.info("Reset from button")
            dev.config.init_config() # TODO
            reset()

    async def __setup_button(self):
        hw.log.debug("Setting up system button ...")
        pin = Pin(hw.SYS_BUTTON_PIN, Pin.IN, Pin.PULL_UP)
        pb = Pushbutton(pin)
        pb.long_func(self.__long_press)
        pb.double_func(self.__double_press)
        create_task(self.__state_clean())

    async def __state_clean(self):
        while True:
            await sleep(1)
            if self.__state_start > 0:
                now = time()
                if now - self.__state_start > SYS_STATE_TIMEOUT:
                    hw.log.debug("Clean up state")
                    self.__state_start = 0
                    dev.state = SYS_STATE_NONE
                    self.__setup_led()

    async def __setup_wifi(self):
        hw.log.debug("Setting up wifi ...")
        if hw.WIFI:
            from wifi import Wifi
            wifi = Wifi(hostname = hw.DEVICE_NAME, pin = hw.WIFI_LED_PIN)
            dev.OPERATORS.append(wifi)
            if await wifi.async_connect():
                hw.log.debug(wifi.get_info())
            else:
                hw.log.error("Wifi connectionf failed")
            create_task(wifi.monitor())

    async def __setup_devices(self):
        hw.log.debug("Setting up device ...")
        from sensor import SensorProcess
        sensor_process = SensorProcess()
        sensor_process.setup(dev.CONSUMERS, dev.SENSORS, dev.IRQ_SENSORS)
        dev.opc.setup(dev.OPERATORS)
        create_task(self.__ntp_update())
        create_task(self.__gc())

    async def __ntp_update(self):
        hw.log.debug("Starting ntp update job")
        while True:
            try:
                await sleep(hw.NTP_INTERVAL)
                if hw.NTP:
                    import ntptime
                    if dev.config.ntphost is not None and dev.config.ntphost != ntptime.host:
                        ntptime.host = dev.config.ntphost
                    hw.log.debug("Update time")
                    ntptime.settime()
            except: #pylint: disable=bare-except
                pass

    async def __gc(self):
        hw.log.debug("Starting ntp update job")
        while True:
            try:
                hw.log.debug("GC")
                mem_info()
                collect()
                mem_info()
                await sleep(hw.GC_INTERVAL)
            except BaseException as e:
                hw.log.error("GC exception %s", e)

    async def __setup_scheduler(self):
        if hw.SCHEDULER:
            hw.log.debug("Setting up cron ...")
            from scheduler import Scheduler
            scheduler = Scheduler(dev.opc)
            dev.OPERATORS.append(scheduler)
            scheduler.setup()

    async def __setup_mqtt(self):
        hw.log.debug("Setting up mqtt ...")
        if hw.MQTT and hw.WIFI:
            from mqtt import Mqtt
            mqtt = Mqtt(dev.opc)
            dev.OPERATORS.append(mqtt)
            dev.CONSUMERS.append(mqtt)
            dev.opc.set_mqtt(mqtt)
            mqtt.setup()

    async def __setup_ble(self):
        if hw.BLE_UART:
            hw.log.debug("Setting up bluebooth ...")
            from ble_uart import BLEUART
            uart = BLEUART(dev.opc, hw.TYPE)
            dev.CONSUMERS.append(uart)

    async def __setup_http(self):
        if hw.HTTP and hw.WIFI:
            hw.log.debug("Setting up http ...")
            from http import http_run
            http_run(dev.opc)

