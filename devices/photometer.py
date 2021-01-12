# Light sensor
from machine import Pin, ADC
from sensor import Producer

class Photometer(Producer):
    def __init__(self, pin):
        Producer.__init__(self, 60000)
        self.__light = ADC(Pin(pin))
        self.__light.atten(ADC.ATTN_11DB)
        self.add_sensor("light", self.get_light)

    def get_light(self): # return 1-100%， more light, highter %
        if self.__light is None:
            return None
        v = (4095 - self.__light.read())/4095 * 100
        return v

