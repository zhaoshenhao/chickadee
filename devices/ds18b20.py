# Class for DS18B20 温度传感器
from machine import Pin
from sensor import Producer
from onewire import OneWire
from ds18x20 import DS18X20

class Ds18b20(Device):
    def __init__(self, pin):
        Producer.__init__(self, 'ds18b20', 60000)
        ow = OneWire(Pin(pin))
        self.__ds = DS18X20(ow)
        self.__rom = self.__ds.scan()
        self.add_sensor("temperature", self.get_temperature)

    def get_temperature(self):
        if self.__ds == None or self.__rom == None or len(self.__rom) <= 0:
            return None
        self.__ds.convert_temp()
        return self.__ds.read_temp(self.__rom[0])

