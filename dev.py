#设备配置
from op import Controller
from sensor import SensorProcess
from sys_op import SysOp
from consumer import DefaultConsumer
from relay import Relay
from dht11 import Dht11
from pir import Pir

#默认配置，请勿修改
# 配置主控
opc = Controller()

# 配置传感器处理进程
sensor_process = SensorProcess()

# 配置可操作设备列表
OPERATORS = []
# 传感器消费者列表
CONSUMERS = []
# 传感器列表
SENSORS = []
# IRQ 传感器列表
IRQ_SENSORS = []

# 配置系统默认操作
config = SysOp(opc)
OPERATORS.append(config)

# 配置传感器消费者
default_consumer = DefaultConsumer()
CONSUMERS.append(default_consumer)
OPERATORS.append(default_consumer)

#以下代码引入需要配置的设备
# 可操控设备
OPERATORS.append(Relay(2, 'relay-1'))

# 传感器设备
SENSORS.append(Dht11(27, 'dht11-1'))

# IRQ 传感器设备
IRQ_SENSORS.append(Pir(22, 'pir-1'))

state = 0
