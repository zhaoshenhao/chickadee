# Config operations
from op import Operator, result, GET, SET
from file import load_json, dump_json
from uasyncio import sleep

class ConfigOp(Operator):
    def __init__(self, name, fn):
        self.__fn = fn
        self.__config = None
        Operator.__init__(self, name)
        self.add_command(self.__get, GET, 'config')
        self.add_command(self.__set, SET, 'config')

    async def __reload_config(self):
        await sleep(0)
        return result()

    async def __set(self, c):
        self.__config = c
        if self.__check_config():
            if self.__save():
                return await self.__reload_config()
            else:
                return result(500, "Save %s failed" % self.__fn)
        else:
            return result(400, "Invalid config, not saved")

    async def __get(self, _):
        v = self.load(True)
        if v is None:
            return result(500, "Load %s failed" % self.__fn)
        return result(200, None, v)

    def load(self, force = False):
        if self.__config == None or force:
            self.__load()
        return self.__config

    def __check_config(self):
        return True
    
    def __init_defaults(self):
        return 0

    def __load(self):
        self.__config = load_json(self.__fn)
        if self.__init_defaults() > 0:
            self.__save()
        return self.__config

    def __save(self):
        return dump_json(self.__config, self.__fn)

