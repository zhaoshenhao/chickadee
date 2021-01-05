from machine import Pin, PWM
from relay import Relay
from sensor import Producer
import uasyncio as asyncio
from micropython import const

ON = const(1023)
OFF = const(0)

class Dimmer(Relay):
    def __init__(self, pin, freq = 5000):
        self.__pin = pin
        self.__freq = freq
        self.__dimmer = PWM(Pin(self.__pin), freq=self.__freq)
        self.__duty = self.__dimmer.duty()
        Producer.__init__(self, 'dimmer')
        self.add_sensor("dimmer", self.get_power)

    def get_power(self):
        return self.__dimmer.duty() / ON

    def on(self):
        self.__duty = ON
        self.__dimmer.duty(self.__duty)

    def off(self):
        self.__duty = OFF
        self.__dimmer.duty(self.__duty)

    def get_pin(self):
        return self.__pin

    def get_freq(self):
        return self.__freq

    def get_dimmer(self):
        return self.__dimmer

    def get_duty(self):
        return self.__duty

    def set_duty(self, duty):
        if duty < OFF:
            self.__duty = OFF
        elif duty > ON:
            self.__duty = ON
        else:
            self.__duty = duty
        self.__dimmer.duty(self.__duty)

    def flip(self):
        if self.__duty == ON:
            self.__duty = OFF
        else:
            self.__duty = ON
        self.__dimmer.duty(self.__duty)

    async def async_pulse(self, fade_tm = 10, interval = 1000):
        for i in range(100):
            self.set_duty(int(i * 11))
            await asyncio.sleep_ms(fade_tm)
        for i in reversed((range(100))):
            self.set_duty(int(i * 11))
            await asyncio.sleep_ms(fade_tm)
        await asyncio.sleep_ms(interval)

    # This function contains bug. Only works after reboot
    async def async_fading(self, fade_tm = 10, interval = 1000):
        self.__async_fading = True
        while self.__async_fading:
            await self.async_pulse(fade_tm, interval)
        self.off()

    def stop_async_fading(self):
        self.__async_fading = False

