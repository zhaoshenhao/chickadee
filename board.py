# The device class contains all necessary generic device operation
from uasyncio import create_task, sleep, get_event_loop
import hw, dev
from time import time
from machine import Pin,Timer,freq, reset
from primitives.pushbutton import Pushbutton
from utils import singleton, set_gc
from micropython import const, mem_info

LOWER_POWER_FEQ = const(40000000)
SYS_STATE_NONE = const(0)
SYS_STATE_REBOOT = const(1)
SYS_STATE_WIFI = const(2)
SYS_STATE_RESET = const(3)
SYS_STATE_TIMEOUT = const(30) # 系统状态超时，系统进入某种状态，比如重启，没有下一步操作，超时后返回常规状态

@singleton
class Board:
    def __init__(self):
        from relay import Relay
        self.__sys_state = SYS_STATE_NONE
        self.__led = Relay(hw.WIFI_LED_PIN)
        self.__in_error_mode = False
        self.__state_start = 0

    async def start(self):
        try:
            hw.log.info("Starting device...")
            from gc import collect
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
        except Exception as e:
            hw.log.error("Start device failed! Exception: %s", e)
            hw.log.info("Entering error mode")
            freq(LOWER_POWER_FEQ)
            self.__in_error_mode = True
            self.__setup_led()
            raise e
        get_event_loop().run_forever()

    def __setup_led(self):
        self.__led.stop_async_blink()
        if self.__sys_state == SYS_STATE_REBOOT:
            create_task(self.__led.async_blink(200, 200))
        elif self.__sys_state == SYS_STATE_RESET:
            create_task(self.__led.async_blink(100, 100))
        elif self.__in_error_mode:
            create_task(self.__led.async_blink(100, 5000))

    def __long_press(self):
        '''
        配置长按操作
        '''
        self.__state_start = time()
        if self.__sys_state == SYS_STATE_NONE:
            self.__sys_state = SYS_STATE_REBOOT
        elif self.__sys_state == SYS_STATE_REBOOT:
            self.__sys_state = SYS_STATE_RESET
        else:
            self.__sys_state = SYS_STATE_NONE
            self.__state_start = 0
        self.__setup_led()

    def __double_press(self):
        '''
        配置短按操作
        '''
        if self.__sys_state == SYS_STATE_REBOOT:
            hw.log.info("Reboot from button")
            reset()
        elif self.__sys_state == SYS_STATE_RESET:
            hw.log.info("Reset from button")
            dev.config.init_config()
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
                    self.__sys_state = SYS_STATE_NONE
                    self.__setup_led()

    async def __setup_wifi(self):
        hw.log.debug("Setting up wifi ...")
        if hw.WIFI:
            from wifi import Wifi
            wifi = Wifi(hostname = hw.DEVICE_NAME, pin = hw.WIFI_LED_PIN)
            dev.OPERATORS.append(wifi)
            if wifi.connect():
                hw.log.debug(wifi.get_info())
            else:
                hw.log.error("Wifi connectionf failed")
            create_task(wifi.monitor())

    async def __setup_devices(self):
        hw.log.debug("Setting up device ...")
        from sensor import SensorProcess
        sensor_process = SensorProcess()
        sensor_process.setup(dev.CONSUMERS, dev.SENSORS)
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
                    if dev.config.ntphost != None and dev.config.ntphost != ntptime.host:
                        ntptime.host = dev.config.ntphost
                    hw.log.debug("Update time")
                    ntptime.settime()
            except: #NOSONAR
                pass

    async def __gc(self):
        hw.log.debug("Starting ntp update job")
        from gc import collect
        while True:
            try:
                await sleep(hw.GC_INTERVAL)
                hw.log.debug("GC")
                mem_info()
                collect()
                mem_info()
            except Exception as e:
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
            mqtt.connect()
            dev.opc.set_mqtt(mqtt)

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

