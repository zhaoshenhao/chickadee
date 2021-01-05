import logging
from wifi import Wifi
from hw import HTTP_PORT, log
from config import Config
from scheduler import Scheduler
from sys_op import SysOp
from consumer import DefaultConsumer
from relay import Relay
from http import http_run
from op import Controller

logging._level = logging.DEBUG
opc = Controller()
ops = []
sch = Scheduler()
sch.setup(opc)
ops.append(Wifi())
ops.append(Config())
ops.append(sch)
ops.append(Relay(2))
ops.append(SysOp(opc))
ops.append(DefaultConsumer())
opc.setup(ops)
print(opc.commands.keys())

if __name__ == '__main__':
    wifi = Wifi()
    wifi.connect()
    http_run(opc, True)
