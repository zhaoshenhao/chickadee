# The device class contains all necessary generic device operation
from time import time
from machine import Pin,Timer,freq, reset
import uasyncio as asyncio
import hw, dev
from primitives.pushbutton import Pushbutton
from config import Config
from sensor import SensorProcess
from op import Controller
from consumer import DefaultConsumer
from scheduler import Scheduler
#from ble_uart_peripheral import BleUart
from utils import singleton, set_gc
from wifi import Wifi
from sys_op import SysOp
from relay import Relay
from micropython import const, mem_info
from gc import collect
import ntptime

LOWER_POWER_FEQ = const(40000000)
SYS_STATE_NONE = const(0)
SYS_STATE_REBOOT = const(1)
SYS_STATE_WIFI = const(2)
SYS_STATE_RESET = const(3)
SYS_STATE_TIMEOUT = const(30) # 系统状态超时，系统进入某种状态，比如重启，没有下一步操作，超时后返回常规状态

'''
系统提示灯
    重启确认: 快速闪烁 200 ms 间隔
    重置确认: 更快速闪烁 100 ms 间隔
    WIFI配置: 闪烁 300 ms 间隔
    出错状态: 非常慢的闪烁，亮 100ms，暗5秒
    无线网络连接中: 闪烁，300ms间隔，参见 wifi.py

系统按钮操作：
    进入系统操作状态: 长按(按住超过5秒)，如果没有任何操作，10秒后解除回到原先状态
    软重启: 进入系统操作状态后短双击
    进入WIFI配置: 再次长按，提示灯闪烁加快，短双击
    进入系统重置：在进入WIFI配置后，再次长按，提示灯闪烁加快，短双击
'''
import tinyweb
app = tinyweb.webserver()
@app.catchall()
async def index(request, response):
    # Start HTTP response with content-type text/html
    await response.start_html()
    # Send actual HTML page
    await response.send('<html><body><h1>Hello, world! (<a href="/table">table</a>)</h1></html>\n')

@singleton
class Board:
    def __init__(self):
        self.__config = Config()
        self.__sensor_process = None
        self.__sys_state = SYS_STATE_NONE
        self.__led = Relay(hw.WIFI_LED_PIN)
        self.__in_error_mode = False
        self.__state_start = 0
        self.__opc = Controller()
        self.__sys_op = SysOp(self.__opc)

    @property
    def config(self):
        return self.__config

    async def start(self):
        try:
            hw.log.info("Starting device...")
            set_gc()
            collect()
            await self.__setup_button()
            collect()
            await self.__setup_wifi()
            collect()
            await self.__setup_ble()
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
        asyncio.get_event_loop().run_forever()

    def __setup_led(self):
        self.__led.stop_async_blink()
        if self.__sys_state == SYS_STATE_REBOOT:
            asyncio.create_task(self.__led.async_blink(200, 200))
        elif self.__sys_state == SYS_STATE_RESET:
            asyncio.create_task(self.__led.async_blink(100, 100))
        elif self.__in_error_mode:
            asyncio.create_task(self.__led.async_blink(100, 5000))

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
            self.__config.init_config()
            reset()

    async def __setup_button(self):
        hw.log.debug("Setting up system button ...")
        pin = Pin(hw.SYS_BUTTON_PIN, Pin.IN, Pin.PULL_UP)
        pb = Pushbutton(pin)
        pb.long_func(self.__long_press)
        pb.double_func(self.__double_press)
        asyncio.create_task(self.__state_clean())

    async def __state_clean(self):
        while True:
            await asyncio.sleep(1)
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
            self.__wifi = Wifi(hostname = hw.DEVICE_NAME, pin = hw.WIFI_LED_PIN)
            if self.__wifi.connect():
                self.__wifi.info()
                asyncio.create_task(self.__wifi.monitor())
            else:
                # TODO setup AP
                pass

    async def __setup_ble(self):
        hw.log.debug("Setting up bluebooth ...")
        # TODO
        '''
        #if self.__config.ble_enabled:
        #    self._ble_uart = BleUart(self.__config.device_name)
        #    self._ble_uart.irq(self._op)
        '''

    async def __setup_devices(self):
        hw.log.debug("Setting up device ...")
        self.__sensor_process = SensorProcess()
        consumers = []
        consumers.append(DefaultConsumer())
        self.__sensor_process.setup(consumers, dev.DEVICES)
        ops = []
        ops.append(self.__scheduler)
        ops.append(self.__config)
        ops.append(self.__wifi)
        ops.append(self.__sys_op)
        self.__opc.setup(ops)
        asyncio.create_task(self.__ntp_update())
        asyncio.create_task(self.__gc())

    async def __ntp_update(self):
        hw.log.debug("Setup ntp update job")
        while True:
            try:
                await asyncio.sleep(hw.NTP_INTERVAL)
                if hw.NTP:
                    if self.__config.ntphost != None and self.__config.ntphost != ntptime.host:
                        ntptime.host = self.__config.ntphost
                    hw.log.debug("Update time")
                    ntptime.settime()
            except: #NOSONAR
                pass

    async def __gc(self):
        while True:
            try:
                await asyncio.sleep(hw.GC_INTERVAL)
                hw.log.debug("GC")
                mem_info()
                collect()
                mem_info()
            except Exception as e:
                hw.log.error("GC exception %s", e)

    async def __setup_scheduler(self):
        hw.log.debug("Setting up cron ...")
        self.__scheduler = Scheduler()
        self.__scheduler.setup(self.__opc)

    async def __setup_mqtt(self):
        from mqtt import MQTTClient
        client = MQTTClient('192.168.1.1', port=1883)
        hw.log.debug("Setting up mqtt ...")
        # TODO

    async def __setup_http(self):
        # TODO
        hw.log.debug("Setting up http ...")
        app.run(host='0.0.0.0', port=hw.HTTP_PORT, loop_forever=False)

