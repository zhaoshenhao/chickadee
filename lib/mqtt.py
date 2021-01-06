from mqtt_lib import MQTTClient
from hw import DEVICE_NAME, log
from config_op import ConfigOp
from op import GET, SET, result, AUTH_ERR, Operator, delayed_task
from uasyncio import sleep, create_task
from utils import singleton
from ujson import loads, dumps
from consumer import Consumer

CMD_TOPIC = "c/" + DEVICE_NAME
CONFIG_NAME = "/dat/mqtt.json"
HOST = 'host'
PORT = 'port'
USER = 'user'
PASSWORD = 'password'
TOPIC = 'topic'
ENABLED = 'enabled'
RECONNECT_MSG = "Reconnect mqtt after 5 seconds"

@singleton
class Mqtt(ConfigOp, Consumer):
    def __init__(self, opc):
        ConfigOp.__init__(self, 'mqtt', CONFIG_NAME)
        self.add_command(self.__get_info, GET)
        self.__client = None
        self.__valid_config = False
        self.__with_auth = False
        self.__opc = opc
        self.add_command(self.__reconnect, SET, 'reconnect')

    async def consume(self, data):
        self.publish(data)
        sleep(0)

    async def __msg_op(self, json):
        r = await self.__opc.op_request(json)
        self.publish(r)

    async def __get_info(self, _):
        v = self.get_info()
        await sleep(0)
        return result(200, None, v)

    async def __reload_config(self): # NOSONAR
        await delayed_task('5000', self.connect, (True, True))
        return result(200, None, RECONNECT_MSG)

    async def __reconnect(self, _):
        await delayed_task('5000', self.connect, (True))
        return result(200, None, RECONNECT_MSG)

    def __suback_cb(self, msg_id, qos): #NOSONAR
        log.info('SUBACK ID = %r, Accepted QOS = %r' % (msg_id, qos))
    
    def __con_cb(self, connected): #NOSONAR
        log.info("Connected. Subscribing topic now")
        if connected:
            self.__client.subscribe(CMD_TOPIC)

    def __auth(self, json):
        if 't' not in json:
            log.warning("No token found")
            return False
        return self.__opc.auth(json['t'])

    def __msg_cb(self, topic, pay): #NOSONAR
        s = pay.decode("utf-8")
        log.info('Received %s: %s' % (topic.decode("utf-8"), s))
        try:
            json = loads(s)
            if not self.__auth(json):
                self.publish(AUTH_ERR)
                return
            if self.__opc is not None:
                create_task(self.__msg_op(json))
        except Exception as e:
            m = "Process message failed: %r" % e
            log.error(m)
            self.publish(result(500, m))

    def publish(self, ret, retain = False, qos = 0):
        ret['i'] = DEVICE_NAME
        return self.publish_str(dumps(ret), retain, qos)

    def publish_str(self, payload, retain = False, qos = 0):
        if self.is_connected():
            return self.__client.publish(self.config_item(TOPIC), payload, retain, qos)
        return None

    def config_item(self, name, def_val = None):
        if self.__config is None or name not in self.__config:
            return def_val
        else:
            return self.__config[name]

    def get_info(self):
        return {
            'enabled': self.config_item(ENABLED, False),
            'connected': self.is_connected(),
            'config_valid': self.__valid_config,
            'with_auth': self.__with_auth,
            'client-id': DEVICE_NAME,
            'host': self.config_item(HOST),
            'port': self.config_item(PORT, 1883),
            'user': self.config_item(USER),
            'password': self.config_item(PASSWORD),
            'sensor-topic': self.config_item(TOPIC),
            'command-topic': CMD_TOPIC
        }

    def disconnect(self):
        if self.__client != None and self.__client.isconnected():
            self.__client.disconnect()

    def __check_config(self):
        if self.config_item(HOST) is None or self.config_item(TOPIC) is None:
            self.__valid_config = False
            self.__with_auth = False
        else:
            self.__valid_config = True
            self.__with_auth = (self.config_item(USER) is not None and self.config_item(PASSWORD) is not None)

    def is_connected(self):
        return self.__client is not None and self.__client.isconnected()

    def connect(self, force = False, reload = False):
        try:
            return self.__connect(force, reload)
        except Exception as e:
            log.warning("Mqtt connection exception: %r", e)
            raise e
            return False
    
    def __connect(self, force = False, reload = False):
        if self.is_connected() and not force and not reload:
            return True
        self.disconnect()
        self.load(reload)
        print(self.__config)
        self.__check_config()
        if self.__valid_config:
            if self.config_item(ENABLED, False):
                self.__client = MQTTClient(self.config_item(HOST), self.config_item(PORT))
            else:
                log.info("MQTT disabled")
                return False
        else:
            log.error("Invalid mqtt config")
            return False
        if self.__with_auth:
            self.__client.connect(DEVICE_NAME, user = self.config_item(USER), password = self.config_item(PASSWORD))
        else:
            self.__client.connect(DEVICE_NAME)
        self.__client.set_connected_callback(self.__con_cb)
        self.__client.set_suback_callback(self.__suback_cb)
        self.__client.set_message_callback(self.__msg_cb)
        return True
