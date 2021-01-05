'''
系统定时任务执行器（定时器）
基于 https://github.com/peterhinch/micropython-async/blob/master/v3/docs/SCHEDULE.md

基本设计:
1. 使用类似Unix cron的方式定义定时任务，精度到秒
2. 定时任务以cron.json的格式保持如下
[
    {
        "name": "test 1",                名称
        "schedule": "* * * * * *",       类似Unix-cron的定时：sec min hr day mon wday
        "params": {                      参数
            "device": "info",            操作器（Operator），参见op.py
            "command": "echo",                操作（Command），参见op.py
            "params": "Hi"                 参数（必须是op接受参数）
        }
    }
]
3. 定时任务器接受一次性任务，格式如同cron.json里的单个任务，但会被设定为只被执行一次
4. 定时器是一个Operator，支持如下命令：set，set，set-one-time-job，delete-one-time-jobs，delete-crons(清除运行的Cron和保持的cron文件
'''

import uasyncio as asyncio
from ure import compile
from sched.cron import cron
from sched.sched import schedule
from utils import singleton
from config_op import ConfigOp
from op import result, CODE, SET, DELETE
from hw import log

SINGLE = compile(r"^\d+$")
ENUM = compile(r"^\d+(,\d)+$")
RANGE = compile(r"^\d+\-\d+\/\d+$")
SCHEDULE = "schedule"
PARAMS = "params"
INVALID_VAL = "Invalid %s value %s."
CRON_FILE = "/dat/cron.json"

def cancel_task(t):
    try:
        if t is not None:
            t.cancel()
    except Exception as e: # NOSONAR
        pass

@singleton
class Scheduler(ConfigOp):
    def __init__(self):
        self._opc = None
        self.__cron = []
        self.__onetime = []
        ConfigOp.__init__(self, 'cron', CRON_FILE)
        self.add_command(self.__cleanup_cron, DELETE)
        self.add_command(self.__add_one_time_job, SET, 'at')
        self.add_command(self.__cleanup_onetime, DELETE, 'at')

    async def __add_one_time_job(self, c):
        log.debug("Add one time job: %s" % c)
        self.__create_scheduler(c, True)
        return result()

    async def op(self, params):
        log.debug("Run scheduled job with param: %s" % params)
        x = await self.__opc.op_request(params)
        if x[CODE] == 200:
            log.info("Run scheduled job done: %s" % x)
        else:
            log.warning("Run scheduled job failed: %s" % x)

    def __create_scheduler(self, j, onetime=False):
        log.debug("create cron item %s", j)
        (sec, m, hr, mday, mon, wday) = parse(j[SCHEDULE])
        p = j[PARAMS]
        if onetime:
            t = asyncio.create_task(schedule(self.op, p, secs = sec, mins = m, hrs = hr, mday = mday, month = mon, wday = wday, times = 1))
            self.__onetime.append(t)
        else:
            t = asyncio.create_task(schedule(self.op, p, secs = sec, mins = m, hrs = hr, mday = mday, month = mon, wday = wday))
            self.__cron.append(t)

    async def __reload_config(self): # NOSONAR
        try:
            self.__load_cron()
            return result()
        except: #NOSONAR
            return result(500, "Reload config failed")

    def __load_cron(self):
        log.debug("Load cron jobs")
        self.cleanup_cron()
        js = self.load()
        try:
            for j in js:
                self.__create_scheduler(j, False)
        except Exception as e:
            self.cleanup_cron()
            log.error("Load cron failed")
            raise e

    def setup(self, opc):
        self.__opc = opc
        self.__load_cron()

    async def __cleanup_cron(self, _):
        await self.cleanup_cron()
        return result()

    async def cleanup_cron(self):
        log.debug("Clean up cron job")
        if self.__cron is not None and len(self.__cron) > 0:
            for t in self.__cron:
                cancel_task(t)
            self.__cron.clear()
        self.__cron = []
        await self.__set([])

    async def __cleanup_onetime(self, _):
        self.cleanup_onetime()
        await asyncio.sleep(0)
        return result()

    async def cleanup_onetime(self):
        log.debug("Clean up one time job")
        if self.__onetime is not None and len(self.__onetime) > 0:
            for t in self.__onetime:
                cancel_task(t)
            self.__onetime.clear()
            self.__onetime = []
        await asyncio.sleep(0)

def error(item, val = None):
    if val is None:
        raise ValueError("Invalide cron item %s." % item)
    else:
        raise ValueError("Invalid %s value %s." % (item, val))

def parse(str):
    l = str.split()
    if len(l) == 6:
        sec = _parse_col(0, 59, l[0], "second")
        if sec == None:
            sec = range(0, 60, 1)
        m = _parse_col(0, 59, l[1], "minute")
        if m is None:
            m = range(0, 60, 1)
        hr = _parse_col(0, 23, l[2], "hour")
        if hr == None:
            hr = range(0, 23, 1)
        mday = _parse_col(1, 31, l[3], "day")
        mon  = _parse_col(1, 12, l[4], "month")
        wday = _parse_col(0, 6, l[5], "week day")
        return sec, m, hr, mday, mon, wday
    error(str)

def _to_int(min, max, str, name):
    v = int(str)
    if v >=min and v <= max:
        return v
    raise ValueError(INVALID_VAL % (name, str))

def _to_int_list(min, max, str, name):
    l = []
    ls = None
    ls = str.split(",")
    if ls is not None and len(ls) > 0:
        for s in ls:
            v = _to_int(min, max, s, name)
            if v is None:
                raise ValueError(INVALID_VAL % (name, str))
            l.append(v)
        return l
    raise ValueError(INVALID_VAL % (name, str))

def _to_int_range(min, max, str, name):
    ls = str.replace('/', '-').split('-')
    if len(ls) == 3:
        start = _to_int(min, max, ls[0], name)
        end = _to_int(min, max, ls[1], name)
        step = _to_int(min, max, ls[2], name)
        if start < end:
            return range(start, end+1, step)
    raise ValueError(INVALID_VAL % (name, str))

def _get_range(name):
    if name == 'second' or name == 'minute':
        return range(0, 60, 1)
    if name == 'hour':
        return range(0, 24, 1)
    return None

def _parse_col(min, max, str, name):
    if "*" == str:
        return _get_range(name)
    if SINGLE.match(str):
        return _to_int(min, max, str, name)
    if ENUM.match(str):
        return _to_int_list(min, max, str, name)
    if RANGE.match(str):
        return _to_int_range(min, max, str, name)
    raise ValueError(INVALID_VAL % (name, str))

