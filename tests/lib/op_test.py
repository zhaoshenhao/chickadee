from op import Controller, request
import uasyncio as asyncio
import logging

def one_time_job():
    op = {}
    op['p'] = 'sys/echo'
    op['c'] = 'set'
    op['a'] = 'hi222'
    job ={}
    job['name'] = 'onetime'
    job['schedule'] = "0-59/15 * * * * *"
    job['params'] = op
    return job

async def test(opc):
    import ujson
    x = await opc.int_op('sys/config', 'get', None)
    print(x)
    x = await opc.int_op('wifi/config', 'get', None)
    print(x)
    x = await opc.int_op('cron/config', 'get', None)
    print(x)
    x = await opc.int_op('sys/info', 'get', None)
    print(x)
    r = request('sys/echo', 'set', 'Hi')
    x = await opc.op_request(r, False)
    print(x)
    r = request('cron/at', 'set', one_time_job())
    x = await opc.op_request(r, False)
    print(x)
    asyncio.sleep(1)

logging._level = logging.DEBUG
opc = Controller()
ops = []

from wifi import Wifi
ops.append(Wifi('ybb-home'))

from scheduler import Scheduler
ops.append(Scheduler(opc))

from sys_op import SysOp
ops.append(SysOp(opc))

from consumer import DefaultConsumer
ops.append(DefaultConsumer())

opc.setup(ops)
print(opc.commands.keys())
try:
    asyncio.run(test(opc))
finally:
    asyncio.new_event_loop()
