from tinyweb import webserver, HTTPException
from wifi import Wifi
from hw import HTTP_PORT, log
from ujson import loads, dumps
from config import Config
from scheduler import Scheduler
from sys_op import SysOp
from consumer import DefaultConsumer
import logging
from op import Controller, CODE, VALUE, GET, SET, DELETE, result
from utils import is_str_empty
from relay import Relay

app = webserver()

BGET = b'GET'
BPOST = b'POST'
BPUT = b'PUT'
TOKEN = b'token'
BDELETE = b'DELETE'

logging._level = logging.DEBUG
opc = Controller()
ops = []
sch = Scheduler()
sch.setup(opc)
ops.append(Wifi())
ops.append(Config())
ops.append(sch)
ops.append(Relay(2))
ops.append(SysOp(opc))
ops.append(DefaultConsumer())
opc.setup(ops)
print(opc.commands.keys())

async def parse_request(req):
    m = GET
    if req.method == BPOST or req.method == BPUT:
        m = SET
    elif req.method == BDELETE:
        m = DELETE
    #req.read_headers([TOKEN])
    p = req.path.decode("utf-8")[1:]
    q = req.query_string
    t = None
    if TOKEN in req.headers:
        t = req.headers[TOKEN].decode("utf-8")
    d = await req.read_parse_form_data()
    return t, p, m, d, q

@app.catchall()
async def index(request, response):
    try:
        t, p, m, d, q = await parse_request(request)
        log.debug({"t": t, "p": p, "m": m, "d": d, "q": q})
        r = await opc.op(p, m, d)
    except HTTPException as e:
        raise e
    except: # NOSONAR
        r = result(500, str(e))
    code = r[CODE]
    if 200 <= code and code <= 299:
        v = r[VALUE]
        if v is None:
            s = ""
        else:
            s = dumps(v)
    else:
        r.pop(VALUE)
        s = dumps(r)
    response.code = r[CODE]
    # Start HTTP response with content-type text/html
    response.add_header('Content-Type', 'application/json')
    response.add_header('Content-Length', str(len(s)))
    await response._send_headers()
    await response.send(s)

def httprun():
    wifi = Wifi()
    wifi.connect()
    app.run(host='0.0.0.0', port=HTTP_PORT)

if __name__ == '__main__':
    httprun()
