# SHT30 高精度温度湿度传感器
import utime
from machine import Pin, I2C
from sensor import Producer

class Sht30(Producer):
    def __init__(self, freq = 100000, sdapin = 13, sclpin = 14):
        self.i2c = I2C(freq=freq, sda=Pin(sdapin), scl=Pin(sclpin))
        addrs = self.i2c.scan()
        if not addrs:
            raise Exception('no SHT3X found at bus on SDA pin %d SCL pin %d' % (sdapin, sclpin)) #NOSONAR
        self.addr = addrs.pop()
        Producer.__init__(self, 'sht30', interval = 60000)
        self.add_sensor("temperature", self.get_temperature)
        self.add_sensor("humidity", self.get_humidity)

    def get_temperature(self):
        t, _ = self.read_temp_humd()
        return t

    def get_humidity(self):
        _, h = self.read_temp_humd()
        return h

    def read_temp_humd(self):
        #status = self.i2c.writeto(self.addr,b'\x2c\x06') #NOSONAR
        _ = self.i2c.writeto(self.addr,b'\x24\x00')
        # delay (20 slow)
        utime.sleep_ms(100)
        # read 6 bytes
        databytes = self.i2c.readfrom(self.addr, 6)
        _ = [databytes[0],databytes[1]]
        _ = [databytes[3],databytes[4]]
        temperature_raw = databytes[0] << 8 | databytes[1]
        temperature = (175.0 * float(temperature_raw) / 65535.0) - 45
        # fahreheit #NOSONAR
        # temperature = (315.0 * float(temperature_raw) / 65535.0) - 49
        humidity_raw = databytes[3] << 8  | databytes[4]
        humidity = (100.0 * float(humidity_raw) / 65535.0)
        return temperature, humidity

