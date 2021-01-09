from ble_uart import BLEUART
import logging
from hw import log
from sys_op import SysOp
from op import Controller
import uasyncio as asyncio
from sensor import SensorProcess
import dev
from consumer import DefaultConsumer

logging._level = logging.DEBUG
opc = Controller()
sp = SensorProcess()
def_consumer = DefaultConsumer()

ops = []
ops.append(SysOp(opc))
ops.append(def_consumer)
opc.setup(ops)

consumers = []
consumers.append(def_consumer)

uart = BLEUART(opc, "ybb-switch-fcf5c429b4bc")
consumers.append(uart)

sp.setup(consumers, dev.SENSORS)

print(opc.commands.keys())

async def test():
    cnt = 0
    while True:
        cnt = cnt + 1
        print("cnt: " + str(cnt))
        await asyncio.sleep(10)

import logging
logging._level = logging.DEBUG
asyncio.run(test())

