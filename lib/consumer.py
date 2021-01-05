'''
Sensor 消费者工具类。配合 sensor.py 使用
'''
from op import Operator, result, GET
from utils import singleton
from uasyncio import sleep

class Consumer:
    def __init__(self):
        # nothing
        pass

    async def consume(self, data):
        await sleep(0)

@singleton
class DefaultConsumer(Operator, Consumer):
    '''
    传感器数据消费者类
    '''
    def __init__(self):
        self.__name = 'sensors'
        Operator.__init__(self, 'sensors')
        self.add_command(self.__get, GET)
        self.__sensors = {}

    @property
    def name(self):
        return self.__name

    async def consume(self, data):
        self.__sensors.update(data)
        sleep(0)

    async def __get(self, _):
        await sleep(0)
        return result(200, None, self.__sensors)

