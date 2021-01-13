from sched.sched import schedule
from utils import singleton
from config_op import ConfigOp
from op import result, CODE, SET, DELETE
import uasyncio as asyncio
from ure import compile #pylint: disable=redefined-builtin
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
    except: #NOSONAR #pylint: disable=bare-except
        pass

@singleton
class Scheduler(ConfigOp):
    def __init__(self, opc):
        self.__opc = opc
        self.__cron = []
        self.__onetime = []
        ConfigOp.__init__(self, 'cron', CRON_FILE)
        self.add_command(self.__cleanup_cron, DELETE)
        self.add_command(self.__add_one_time_job, SET, 'at')
        self.add_command(self.__cleanup_onetime, DELETE, 'at')

    async def __add_one_time_job(self, c):
        log.debug("Add one time job: %s" , c)
        self.__create_scheduler(c, True)
        return result()

    async def op(self, params):
        log.debug("Run scheduled job with param: %s", params)
        x = await self.__opc.op_request(params, False)
        if x[CODE] == 200:
            log.info("Run scheduled job done: %s", x)
        else:
            log.warning("Run scheduled job failed: %s", x)

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
            self.setup()
            return result()
        except: #NOSONAR #pylint: disable=bare-except
            return result(500, "Reload config failed")

    def setup(self):
        try:
            log.debug("Load cron jobs")
            self.cleanup_cron()
            js = self.load()
            for j in js:
                self.__create_scheduler(j, False)
        except BaseException as e: #NOSONAR #pylint: disable=bare-except
            log.error("Load cron failed %r", e)
            self.cleanup_cron()

    async def __cleanup_cron(self, _):
        await self.cleanup_cron(True)
        return result()

    async def cleanup_cron(self, empty_cfg = False):
        log.debug("Clean up cron job")
        if self.__cron is not None and len(self.__cron) > 0:
            for t in self.__cron:
                cancel_task(t)
            self.__cron.clear()
        self.__cron = []
        if empty_cfg:
            await self.__set([])

    async def __cleanup_onetime(self, _):
        log.debug("Clean up one time job")
        if self.__onetime is not None and len(self.__onetime) > 0:
            for t in self.__onetime:
                cancel_task(t)
            self.__onetime.clear()
            self.__onetime = []
        await asyncio.sleep(0)
        return result()

def error(item, val = None):
    if val is None:
        raise ValueError("Invalide cron item %s." % item)
    raise ValueError("Invalid %s value %s." % (item, val))

def parse(s):
    l = s.split()
    if len(l) == 6:
        sec = _parse_col(0, 59, l[0], "second")
        if sec is None:
            sec = range(0, 60, 1)
        m = _parse_col(0, 59, l[1], "minute")
        if m is None:
            m = range(0, 60, 1)
        hr = _parse_col(0, 23, l[2], "hour")
        if hr is None:
            hr = range(0, 23, 1)
        mday = _parse_col(1, 31, l[3], "day")
        mon  = _parse_col(1, 12, l[4], "month")
        wday = _parse_col(0, 6, l[5], "week day")
        return sec, m, hr, mday, mon, wday
    error(s)

def _to_int(mins, imax, s, name):
    v = int(s)
    if mins <= v <= imax:
        return v
    raise ValueError(INVALID_VAL % (name, s))

def _to_int_list(mins, imax, s, name):
    l = []
    ls = None
    ls = s.split(",")
    if ls is not None and len(ls) > 0:
        for s in ls:
            v = _to_int(mins, imax, s, name)
            if v is None:
                raise ValueError(INVALID_VAL % (name, s))
            l.append(v)
        return l
    raise ValueError(INVALID_VAL % (name, s))

def _to_int_range(mins, imax, str1, name):
    ls = str1.replace('/', '-').split('-')
    if len(ls) == 3:
        start = _to_int(mins, imax, ls[0], name)
        end = _to_int(mins, imax, ls[1], name)
        step = _to_int(mins, imax, ls[2], name)
        if start < end:
            return range(start, end+1, step)
    raise ValueError(INVALID_VAL % (name, str1))

def _get_range(name):
    if name in ('second', 'minute'):
        return range(0, 60, 1)
    if name == 'hour':
        return range(0, 24, 1)
    return None

def _parse_col(mins, imax, str1, name):
    if str1 == "*":
        return _get_range(name)
    if SINGLE.match(str1):
        return _to_int(mins, imax, str1, name)
    if ENUM.match(str1):
        return _to_int_list(mins, imax, str1, name)
    if RANGE.match(str1):
        return _to_int_range(mins, imax, str1, name)
    raise ValueError(INVALID_VAL % (name, str1))

