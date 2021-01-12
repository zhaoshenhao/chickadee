from op import Operator, result, GET
from utils import singleton
from uasyncio import sleep

class Consumer: # pylint: disable=too-few-public-methods
    def __init__(self):
        # nothing
        pass

    async def consume(self, _):
        await sleep(0)

@singleton
class DefaultConsumer(Operator, Consumer):
    def __init__(self):
        Consumer.__init__(self)
        self.__name = 'sensors'
        Operator.__init__(self, 'sensors')
        self.add_command(self.__get, GET)
        self.__sensors = {}

    @property
    def name(self):
        return self.__name

    async def consume(self, data):
        d = data['d']
        s = data['s']
        self.__sensors[d] = s
        sleep(0)

    async def __get(self, _):
        await sleep(0)
        return result(200, None, self.__sensors)

