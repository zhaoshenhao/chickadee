'''
设备配置
'''

'''
默认配置，请勿修改
'''
# 配置主控
from op import Controller
opc = Controller()

# 配置传感器处理进程
from sensor import SensorProcess
sensor_process = SensorProcess()

# 配置可操作设备列表
OPERATORS = []
# 传感器消费者列表
CONSUMERS = []
# 传感器列表
SENSORS = []

# 配置系统默认操作
from sys_op import SysOp
config = SysOp(opc)
OPERATORS.append(config)

# 配置传感器消费者
from consumer import DefaultConsumer
default_consumer = DefaultConsumer()
CONSUMERS.append(default_consumer)
OPERATORS.append(default_consumer)

'''
以下代码引入需要配置的设备
'''
# 额外可操控设备
from relay import Relay
OPERATORS.append(Relay(2))

# 额外传感器设备
from dht11 import Dht11
SENSORS.append(Dht11(27))

state = 0