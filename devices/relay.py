# For any relay/switch
from machine import Pin
from utils import singleton
from sensor import Producer
import uasyncio as asyncio
from micropython import const
from op import Operator, result, INVALID_ARGS, SET, GET

ON = const(1)
OFF = const(2)
OP = "op"
ON_MS = 'on-ms'
OFF_MS = 'off-ms'

class Relay(Producer, Operator):
    def __init__(self, pin):
        Producer.__init__(self, "relay", interval = 60000)
        Operator.__init__(self, "relay")
        self.__relay = Pin(pin ,Pin.OUT)
        self.add_sensor("relay", self.get_state)
        self.__async_blinking = False
        self.add_command(self.__op, SET)
        self.add_command(self.__get, GET)

    async def __op(self, p):
        asyncio.sleep(0)
        try:
            mop = p[OP].lower()
            if mop == 'on':
                self.__relay.on()
            elif mop == 'off':
                self.__relay.off()
            elif mop == 'flip':
                self.flip()
            elif mop == 'blink':
                onms = p[ON_MS]
                offms = p[OFF_MS]
                if type(onms) == int and type(offms) == int:
                    asyncio.create_task(self.async_blink(int(onms), int(offms)))
                else:
                    return INVALID_ARGS
            elif mop == 'stop-blink':
                self.stop_async_blink()
            else:
                return INVALID_ARGS
        except Exception as e: #NOSONAR
            print(e)
            return INVALID_ARGS    
        return result(200, None, self.get_state())
    
    async def __get(self, _):
        await asyncio.sleep(0)
        v = self.get_state()
        return result(200, None, v)

    def on(self):
        # 点亮
        self.__relay.on()

    def off(self):
        # 关闭
        self.__relay.off()

    def get_state(self):
        return self.__relay.value()

    def get_relay(self):
        return self.__relay

    def flip(self):
        # 翻转
        if self.__relay.value() == ON:
            self.__relay.off()
        else:
            self.__relay.on()

    async def async_blink(self, on_tm = 200, off_tm = 1000):
        # 异步闪烁
        self.__async_blinking = True
        self.off()
        while self.__async_blinking:
            self.on()
            await asyncio.sleep_ms(on_tm)
            self.off()
            await asyncio.sleep_ms(off_tm)

    def stop_async_blink(self):
        self.__async_blinking = False

