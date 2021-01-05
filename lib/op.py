from uasyncio import Lock
from ujson import dumps, loads
from hw import log
from utils import singleton, is_str_empty

CODE = 'c'
MESSAGE = 'm'
VALUE = 'v'
COMMAND = 'c'
PATH = 'p'
ARGS = 'a'
OP_INFO = "Op %s"
NOT_FOUND = "Op %s not found"
CALL_ERROR =  "Op %s failed: %s"
JSON_ERROR = "Invalid json string: %s.\n%s"
SET = 'set'
GET = 'get'
DELETE = 'delete'

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

op_lock = Lock()

@singleton
class Controller:
    '''
    操作处理中心
    '''
    def __init__(self):
        self.commands = {}

    async def op(self, path, command, param):
        async with op_lock:
            return await self.__op(path, command, param)

    async def __op(self, path, command, param):
        '''
        显式调用，传入operator，command 和参数，适合REST格式。参数必须时command接受的Json格式
        '''
        p = path + ":" + command
        log.debug(OP_INFO, p)
        if p in self.commands:
            h = self.commands[p]
            try:
                return await h(param)
            except Exception as e:
                return result(500, CALL_ERROR % (p, e))
        else:
            return result(404, NOT_FOUND % p)

    async def op_str(self, request):
        '''
        处理 Json String 的请求
        '''
        try:
            return await self.op_request(loads(request))
        except Exception as e:
            return result(400, JSON_ERROR % request, e)

    async def op_request(self, request):
        '''
        处理类似Json的请求，只使用List/Dict/基础类型
        '''
        if COMMAND not in request or PATH not in request or ARGS not in request:
            return result(400, 'Invalid request, no path/cmd/args property.')
        cmd = request[COMMAND]
        path = request[PATH]
        p = request[ARGS]
        return await self.op(path, cmd, p)

    def setup(self, operators):
        for op in operators:
            self.commands.update(op.commands)

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
