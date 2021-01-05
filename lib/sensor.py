# Represent a sensor
import time
import uasyncio as asyncio
from utils import singleton
from primitives import queue
from hw import log, PRINT_SENSOR_DATA

@singleton
class SensorProcess:
    '''
    传感器数据统一处理流程
    '''
    def __init__(self):
        self.__sensor_queue = queue.Queue(10)
        self.__consumers = []

    async def __consume(self, queue):
        while True:
            try:
                result = await queue.get()
                await self.__process_sensor_queue(result)
            except: #NOSONAR
                pass

    async def __process_sensor_queue(self, result):
        if PRINT_SENSOR_DATA:
            log.debug("Process sensor queue: %s", result)
        if self.__consumers is None or len(self.__consumers) <= 0:
            return
        for c in self.__consumers:
            await c.consume(result)

    def setup(self, consumers, producers = [], irq_producers = []):
        # 添加传感器
        if producers is not None and len(producers) > 0:
            for d in producers:
                asyncio.create_task(d.produce(self.__sensor_queue))
        if irq_producers is not None and len(irq_producers) > 0:
            for d in irq_producers:
                #TODO
                pass
        # 添加处理器
        self.__consumers = consumers
        # 运行
        asyncio.create_task(self.__consume(self.__sensor_queue))


class Producer:
    '''
    设备抽象类
    '''
    def __init__(self, name, interval = 30000): # name must be [a-zA-Z_-], interval
        '''
        interval: 设备收集数据间隔，单位ms
        '''
        self.__sensors = []
        self.__prepare = None
        self.__delay = 100 # ms
        self.__interval = interval
        self.__name = name

    async def produce(self, queue):
        '''
        产生传感器数据，发送到处理队列
        '''
        log.debug("Start sensor data producer: %s", self.__name)
        while True:
            vals = await self.async_sensor_values()
            log.debug("Get sensor data")
            await queue.put(vals)
            await asyncio.sleep_ms(self.__interval)

    def add_sensor(self, name, handler):
        s = Sensor(name, handler)
        self.__sensors.append(s)

    def set_prepare_handler(self, fun):
        self.__prepare = fun

    @property
    def sensors(self):
        return self.__sensors

    @property
    def sensor_values(self):
        '''
        同步模式获取值
        '''
        if self.__prepare != None:
            self.__prepare()
            time.sleep_ms(self.__delay)
        l = []
        for s in self.__sensors:
            l.append(s.value)
        v = {}
        v['d'] = self.__name
        v['s'] = l
        return v

    async def async_sensor_values(self):
        '''
        异步模式获取值
        '''
        if self.__prepare != None:
            self.__prepare()
            await asyncio.sleep_ms(self.__delay)
        l = []
        for s in self.__sensors:
            l.append(s.value)
        v = {}
        v['d'] = self.__name
        v['s'] = l
        return v

    def remove_sensor(self, name):
        '''
        异步模式对@propert 支持有问题，此处不用
        '''
        for s in self.__sensors:
            if s.name == name:
                self.__sensors.remove(s)

class Sensor:
    '''
    传感器抽象类
    '''
    def __init__(self, name, handler):
        self.__name = name
        self.__handler = handler

    @property
    def value(self):
        d = {}
        d['n'] = self.__name
        d['v'] = self.__handler()
        return d

    @property
    def name(self):
        return self.__name

    @property
    def handler(self):
        return self.__handler

