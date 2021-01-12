# DHT11 温度、湿度传感器
from machine import Pin
from sensor import Producer
import dht

class Dht11(Producer):
    def __init__(self, pin):
        self._pin = pin
        Producer.__init__(self, 'dht11', 60000, 1000)
        self._dht = dht.DHT11(Pin(self._pin))
        self.add_sensor("temperature", self.get_temperature)
        self.add_sensor("humidity", self.get_humidity)
        self.set_prepare_handler(self.measure)

    def measure(self):
        self._dht.measure()

    def get_temperature(self):
        if self._dht is None:
            return None
        return self._dht.temperature()

    def get_humidity(self):
        if self._dht is None:
            return None
        return self._dht.humidity()

