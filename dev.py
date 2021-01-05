'''
以下代码引入需要配置的设备
'''
DEVICES = []

# 配置传感器设备
from dht11 import Dht11
DEVICES.append(Dht11(27))
