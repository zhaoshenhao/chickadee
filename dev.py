'''
以下代码引入需要配置的设备
'''
# 配置传感器设备
SENSORS = []
from dht11 import Dht11
SENSORS.append(Dht11(27))

# 配置可操作设备
from relay import Relay
OPERATORS = []
OPERATORS.append(Relay(2))