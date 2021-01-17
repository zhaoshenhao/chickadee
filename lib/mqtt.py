from config_op import ConfigOp
from op import GET, SET, result
from uasyncio import sleep, create_task
from utils import singleton, delayed_task, time_stamp
from primitives import queue
from ujson import loads, dumps
from consumer import Consumer
from umqtt.simple import MQTTClient
from utime import time
from hw import DEVICE_NAME, log

CMD_TOPIC = "c/" + DEVICE_NAME
CONFIG_NAME = "/dat/mqtt.json"
OP_LOG_TOPIC = 'o/' + DEVICE_NAME
HOST = 'host'
PORT = 'port'
USER = 'user'
PASSWORD = 'password'
TOPIC = 'topic'
ENABLED = 'enabled'
RECONNECT_MSG = "Reconnect mqtt after 5 seconds"
KEEP_ALIVE = 5
SLEEP_INTERVAL = 1
SSL = False
DEBUG = False
RECONNECT_INTERVAL = 10

@singleton
class Mqtt(ConfigOp, Consumer):
    def __init__(self, opc):
        ConfigOp.__init__(self, 'mqtt', CONFIG_NAME)
        Consumer.__init__(self)
        self.add_command(self.__get_info, GET)
        self.__client = None
        self.__pub_queue = queue.Queue(10)
        self.__connected = False
        self.__last_ping_tm = 0
        self.__valid_config = False
        self.__with_auth = False
        self.__opc = opc
        self.__topic = set()
        self.__sub_cb = None
        self.add_command(self.__reconnect, SET, 'reconnect')

    async def consume(self, data):
        self.publish(data)
        sleep(0)

    async def __get_info(self, _):
        v = self.get_info()
        await sleep(0)
        return result(200, None, v)

    def config_item(self, name, def_val = None):
        if self.__config is None or name not in self.__config:
            return def_val
        return self.__config[name]

    def get_info(self):
        return {
            ENABLED: self.config_item(ENABLED, False),
            'connected': self.is_connected(),
            'config_valid': self.__valid_config,
            'with_auth': self.__with_auth,
            'client-id': DEVICE_NAME,
            HOST: self.config_item(HOST),
            PORT: self.config_item(PORT, 1883),
            USER: self.config_item(USER),
            PASSWORD: self.config_item(PASSWORD),
            'sensor-topic': self.config_item(TOPIC),
            'command-topic': CMD_TOPIC
        }

    async def __reload_config(self): # NOSONAR
        delayed_task(5000, self.connect, (True, True))
        return result(200, None, RECONNECT_MSG)

    async def __reconnect(self, _):
        delayed_task(5000, self.connect, (True))
        return result(200, None, RECONNECT_MSG)

    def __check_config(self):
        if self.config_item(HOST) is None or self.config_item(TOPIC) is None:
            self.__valid_config = False
            self.__with_auth = False
        else:
            self.__valid_config = True
            self.__with_auth = (self.config_item(USER) is not None and self.config_item(PASSWORD) is not None)

    def is_connected(self):
        return self.__client is not None and self.__connected

    def connect(self, force = False, reload = False):
        try:
            return self.__connect(force, reload)
        except BaseException as e:
            log.warning("Mqtt connection exception: %r", e)
            return False

    def __connect(self, force = False, reload = False):
        if self.is_connected() and not force and not reload:
            return True
        self.disconnect()
        self.load(reload)
        self.__check_config()
        if self.__valid_config:
            if self.config_item(ENABLED, False):
                if self.__with_auth:
                    self.__client = MQTTClient(
                        DEVICE_NAME, self.config_item(HOST), self.config_item(PORT),
                        self.config_item(USER), self.config_item(PASSWORD), 0, SSL)
                else:
                    self.__client = MQTTClient(
                        DEVICE_NAME, self.config_item(HOST), self.config_item(PORT),
                        None, None, 0, SSL)
            else:
                log.info("MQTT disabled")
                return False
        else:
            log.error("Invalid mqtt config")
            return False
        self.__client.connect()
        self.__client.DEBUG = DEBUG
        self.__client.set_callback(self.__sub_callback)
        self.__client.subscribe(bytes(CMD_TOPIC, 'utf-8'))
        self.__connected = True
        log.debug("Mqtt broker connected")
        return True

    def disconnect(self):
        log.debug("Disconnect mqtt")
        self.__connected = False
        if self.__client is None:
            return
        try:
            self.__client.disconnect()
        except: #pylint: disable=bare-except
            pass
        self.__client = None

    def publish_op_log(self, p, c, ret):
        x = {'p': p, 'c': c, 'r': ret, 'tm': time_stamp()}
        return self.publish(x, topic = OP_LOG_TOPIC)

    def __sub_callback(self, topic, pay): 
        s = pay.decode("utf-8")
        log.info('Received %s: %s' , topic.decode("utf-8"), s)
        try:
            json = loads(s)
            create_task(self.__opc.op_request(json))
        except BaseException as e:
            m = "Process message failed: %r" % e
            log.error(m)
            self.publish_op_log(None, None, result(500, m))

    def publish(self, ret, retain = False, qos = 0, topic = None):
        t = None
        try:
            ret['i'] = DEVICE_NAME
            if topic is None:
                t = self.config_item(TOPIC)
            else:
                t = topic
            if t is None:
                log.debug("None topic, ignored")
                return
            log.debug("Add msg to pub queue: topic: %s, %r ", t, ret)
            l = {'t': bytes(t, 'utf-8'), 'm': bytes(dumps(ret), 'utf-8'), 'r': retain, 'q': qos}
            self.__pub_queue.put_nowait(l)
        except BaseException as e:
            log.error("Publish to topic %s failed: %r", t, e)

    def __next(self, o):
        if o is not None:
            return o
        try:
            try:
                return self.__pub_queue.get_nowait()
            except: #pylint: disable=bare-except
                return None
        except: #pylint: disable=bare-except
            return None

    async def __int_pub(self, o):
        '''从旧消息或队列里读取，如果qos大于0，且失败，返回未发送得消息'''
        while True:
            m = self.__next(o)
            if m is None:
                return None
            qos = 0
            try:
                qos = m['q']
                if self.is_connected():
                    log.debug("Publish msg %r", m)
                    self.__client.publish(m['t'], m['m'], m['r'])
                    self.__last_ping_tm = time()
                return None
            except BaseException as e:
                log.debug("Publish error: %r", e)
                self.__connected = False
                if qos > 0:
                    return m
                return None

    def __keep_alive(self):
        if time() > self.__last_ping_tm + KEEP_ALIVE:
            try:
                if self.is_connected():
                    log.debug("Mqtt ping")
                    self.__client.ping()
                    self.__last_ping_tm = time()
            except: #pylint: disable=bare-except
                self.__connected = False

    def __int_sub(self):
        try:
            if self.is_connected():
                log.debug("mqtt sub-check")
                self.__client.check_msg()
                self.__last_ping_tm = time()
        except: #pylint: disable=bare-except
            self.__connected = False

    async def __loop(self):
        old_msg = None
        log.debug("Start mqtt loop")
        while True:
            try:
                if self.is_connected():
                    old_msg = await self.__int_pub(old_msg)
                    self.__int_sub()
                    self.__keep_alive()
                else:
                    while not self.is_connected():
                        self.connect()
                        await sleep(RECONNECT_INTERVAL)
            except: #pylint: disable=bare-except
                self.__connected = False # 指示连接错误
            await sleep(SLEEP_INTERVAL)

    def setup(self):
        self.connect()
        create_task(self.__loop())
