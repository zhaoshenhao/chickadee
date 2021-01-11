from uasyncio import Lock, sleep_ms
from ujson import dumps, loads
from hw import log
from utils import singleton, is_str_empty

CODE = 'c'
MESSAGE = 'm'
VALUE = 'v'
COMMAND = 'c'
PATH = 'p'
ARGS = 'a'
TOKEN = 't'
OP_INFO = "Op %s"
NOT_FOUND = "Op %s not found"
CALL_ERROR =  "Op %s failed: %s"
JSON_ERROR = "Invalid json string: %s.\n%s"
SET = 'set'
GET = 'get'
DELETE = 'delete'
GET_TM = 'get-tm'

def request(p, c, a):
    return {
        PATH: p,
        COMMAND: c,
        ARGS: a
    }

def result(c = 200, m = '', v = None):
    return {
        CODE: c,
        MESSAGE: m,
        VALUE: v
    }

INVALID_ARGS = result(400, "Invalid op args")
AUTH_ERR = result(401, "Invalid token")

op_lock = Lock()

@singleton
class Controller:
    '''
    操作处理中心
    '''
    def __init__(self):
        self.commands = {}
        self.__mqtt = None

    async def op(self, token, path, command, param, req_auth = True):
        '''
        操作处理
        req_auth: 内部调用设置为 False
        '''
        r = None
        if req_auth:
            tm = self.tm_auth(token)
            if tm is not None:
                r = tm
            if not self.auth(token):
                r = AUTH_ERR
        if r is None:
            async with op_lock:
                try:
                    r = await self.int_op(path, command, param)
                except Exception as e:
                    msg = CALL_ERROR % (path + ':' + command, e)
                    log.error(msg)
                    r = result(500, msg)
        if self.__mqtt is not None:
            self.__mqtt.publish_op_log(path, command, r)
        return r

    def auth(self, token):
        if token is None:
            return False
        return True # TODO

    def tm_auth(self, token):
        '''
        检查是否是特殊Token，如果是，返回时间戳
        '''
        try:
            if GET_TM == token.lower():
                from utime import time
                return result(200, None, {"tm": time()})
        except: # NOSONAR
            pass
        return None

    async def int_op(self, path, command, param):
        '''
        显式调用，传入operator，command 和参数，适合REST格式。参数必须时command接受的Json格式
        无需认证
        '''
        p = path + ":" + command
        log.debug(OP_INFO, p)
        if p in self.commands:
            h = self.commands[p]
            return await h(param)
        else:
            return result(404, NOT_FOUND % p)

    async def op_request(self, request, req_auth = True):
        '''
        处理类似Json的请求，只使用List/Dict/基础类型
        '''
        if COMMAND not in request or PATH not in request or ARGS not in request:
            return result(400, 'Invalid request, no path/cmd/args property.')
        cmd = request[COMMAND]
        path = request[PATH]
        p = request[ARGS]
        t = None
        if req_auth and TOKEN in request:
            t = request[TOKEN]
        return await self.op(t, path, cmd, p, req_auth)

    def setup(self, operators):
        for op in operators:
            self.commands.update(op.commands)

    def set_mqtt(self, mqtt):
        self.__mqtt = mqtt

class Operator:
    '''
    代表提供命令操作的抽象类，每个需要提供命令的设备需要继承该类
    '''
    def __init__(self, n):
        self.commands = {}
        self.__name = n

    def add_command(self, handler, op = GET, path = None):
        '''
        Only allow get, set and delete
        '''
        if (op != GET and op != SET and op != DELETE):
            raise ValueError("Invalid op: %s" % op)
        if not is_str_empty(path):
            p = self.__name + "/" + path + ":" + op
        else:
            p = self.__name + ":" + op
        self.commands[p] = handler
