import logging
from wifi import Wifi
from hw import log
from scheduler import Scheduler
from sys_op import SysOp
from consumer import DefaultConsumer
from relay import Relay
from http import http_run
from op import Controller
import uasyncio as asyncio

logging._level = logging.DEBUG
opc = Controller()
ops = []
sch = Scheduler(opc)
sch.setup()
ops.append(Wifi('ybb-home'))
ops.append(sch)
ops.append(Relay(2))
ops.append(SysOp(opc))
ops.append(DefaultConsumer())
opc.setup(ops)
print(opc.commands.keys())

async def test():
    wifi = Wifi('ybb-home')
    await wifi.async_connect()
    await http_run(opc, True)

if __name__ == '__main__':
    asyncio.run(test())