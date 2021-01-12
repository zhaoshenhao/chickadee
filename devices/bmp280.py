# BMP280 气压，温度，海拔（误差较大）
from machine import Pin, I2C
from sensor import Producer
from bmp_280 import BMP280

class Bmp280(Producer):
    def __init__(self, pin1, pin2):
        self._pin1 = pin1
        self._pin2 = pin2
        self._i2c = I2C(sda=Pin(16), scl=Pin(17))
        Producer.__init__(self, 'bmp280', 60000)
        self._bmp = BMP280(self._i2c)
        self.add_sensor("temperature", self.get_temperature)
        self.add_sensor("pressure", self.get_pressure)
        self.add_sensor("altitude", self.get_altitude)

    def get_temperature(self):
        if self._bmp is None:
            return None
        return self._bmp.getTemp()

    def get_pressure(self):
        if self._bmp is None:
            return None
        return self._bmp.getPress()

    def get_altitude(self):
        if self._bmp is None:
            return None
        return ((pow((101325 / self.get_pressure()), (1.0 / 5.256)) - 1) * (self.get_temperature() + 273.15)) / 0.0065

