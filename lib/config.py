# Write your code here :-)
from hw import TYPE, NTP_HOST, UNIQUE_ID
from utils import random_string, singleton
from config_op import ConfigOp

LABEL = "label"
SECRET = "secret"
NTPHOST = "ntphost"
CONFIG_FILE = "/dat/config.json"

@singleton
class Config(ConfigOp):
    def __init__(self):
        self.__config = None
        ConfigOp.__init__(self, 'sys', CONFIG_FILE)
        self.commands.pop('sys/config:set') # 取消设置功能

    @property
    def ntphost(self):
        if self.__config != None and NTPHOST in self.__config:
            return self.__config[NTPHOST]
        return NTP_HOST

    @property
    def device_secret(self):
        return self.__config[SECRET]

    @property
    def device_lable(self):
        return self.__config[LABEL]

    def __init_defaults(self, force = False):
        changes = 0
        if self.__config == None:
            self.__config = {}
        if SECRET not in self.__config or force:
            self.__config[SECRET] = random_string(32)
            changes += 1
        if LABEL not in self.__config or force:
            self.__config[LABEL] = self.device_name
            changes += 1
        return changes

    def init_config(self, force = False):
        if self.__init_defaults(force) > 0:
            self.__save()

