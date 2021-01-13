import logging
from mqtt import Mqtt
from wifi import Wifi
from sys_op import SysOp
from op import Controller
import uasyncio as asyncio
from sensor import SensorProcess
from consumer import DefaultConsumer
import dev

logging._level = logging.DEBUG
opc = Controller()
sp = SensorProcess()
def_consumer = DefaultConsumer()

ops = []
wifi = Wifi('ybb-home')
ops.append(wifi)
ops.append(SysOp(opc))
ops.append(def_consumer)
mqtt = Mqtt(opc)
ops.append(mqtt)
opc.setup(ops)
opc.set_mqtt(mqtt)

consumers = []
consumers.append(def_consumer)
consumers.append(mqtt)

print(opc.commands.keys())

async def test():
    await wifi.async_connect()
    print(mqtt.get_info())
    mqtt.setup()
    print(mqtt.get_info())
    sp.setup(consumers, dev.SENSORS)
    cnt = 0
    while True:
        cnt = cnt + 1
        print("cnt: " + str(cnt))
        await asyncio.sleep(10)

asyncio.run(test())
