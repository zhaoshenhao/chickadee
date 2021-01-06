from tinyweb import webserver, HTTPException
from hw import HTTP_PORT
from ujson import dumps
from op import CODE, VALUE, GET, SET, DELETE, result, AUTH_ERR

app = webserver()

BGET = b'GET'
BPOST = b'POST'
BPUT = b'PUT'
TOKEN = b'token'
BDELETE = b'DELETE'

opc = None

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
        if not opc.auth(t):
            r = AUTH_ERR
        else:
            r = await opc.op(p, m, d)
    except HTTPException as e:
        raise e
    except Exception as e1:
        r = result(500, str(e1))
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

def http_run(o, loop_forever=False):
    global opc
    opc = o
    app.run(host='0.0.0.0', port=HTTP_PORT, loop_forever=loop_forever)