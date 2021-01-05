from scheduler import Scheduler, parse
import uasyncio as asyncio

def one_time_job():
    op = {}
    op['p'] = 'sys/echo'
    op['c'] = 'set'
    op['params'] = 'hi222'
    job ={}
    job['name'] = 'onetime'
    job['schedule'] = "0-59/15 * * * * *"
    job['params'] = op
    return job

async def test1():
    from op import OpCenter
    from sys_op import SysOp
    sch = Scheduler()
    opc = OpCenter()
    ops = []
    ops.append(sch)
    ops.append(SysOp(opc))
    opc.setup(ops)
    sch.setup(opc)
    await asyncio.sleep(3)
    x = await opc.op('cron/at', 'set', one_time_job())
    print(x.to_json())
    await asyncio.sleep(12)
    x = await opc.op('cron', 'delete', None)
    print(x.to_json())
    x = await opc.op('cron/at', 'delete', None)
    print(x.to_json())
    await asyncio.sleep(20)

def test0():
    cron1 = parse("* * * * * *")
    print(cron1)
    cron2 = parse("0 0-59/10 0-23/4 2,4 1,3 *")
    print(cron2)
    cron3 = parse("0 1,2 0-23/4 2,4 1,3 *")
    print(cron3)

def demo():
    test0()
    import logging
    logging._level = logging.DEBUG
    try:
        asyncio.run(test1())
    finally:
        asyncio.new_event_loop()

if __name__ == "__main__":
    demo()
