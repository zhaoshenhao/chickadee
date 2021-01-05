# SHT30 高精度温度湿度传感器
from sht30 import Sht30

def demo():
    sht = Sht30()
    print(sht.read_temp_humd())
    print(sht.sensor_values)

if __name__ == "__main__":
    demo()
