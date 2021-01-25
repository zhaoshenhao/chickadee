from tinyweb import webserver
from ujson import dumps #pylint: disable=unused-import
from op import CODE, VALUE, GET, SET, DELETE, result
from sec import Sec
from hw import HTTP_PORT, ENCRYPTED_OUTPUT, ENCRYPTED_INPUT, log

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
    p = req.path.decode("utf-8")[1:]
    q = req.query_string
    t = None
    if TOKEN in req.headers:
        t = req.headers[TOKEN].decode("utf-8")
    d = await req.read_parse_form_data()
    if ENCRYPTED_INPUT:
        st = Sec()
        if d is not None:
            d = st.dec_payload(d)
    return t, p, m, d, q

def enc(data : dict):
    if ENCRYPTED_OUTPUT:
        st = Sec()
        return st.enc_paylaod(data)
    return data

@app.catchall()
async def index(request, response):
    try:
        t, p, m, d, _ = await parse_request(request)
        r = await opc.op(t, p, m, d)
    except BaseException as e: #NOSONAR
        log.debug("Request error: %r", e)
        r = result(500, str(e))
    code = r[CODE]
    if 200 <= code <= 299:
        v = None if VALUE not in r else r[VALUE]
        if v is None:
            s = ""
        else:
            s = dumps(enc(v))
    else:
        if VALUE in r:
            r.pop(VALUE)
        s = dumps(enc(r))
    response.code = r[CODE]
    # Start HTTP response with content-type text/html
    response.add_header('Content-Type', 'application/json')
    response.add_header('Content-Length', str(len(s)))
    await response._send_headers() #pylint: disable=protected-access

    await response.send(s)

def http_run(o, loop_forever=False):
    global opc #pylint: disable=global-statement
    opc = o
    app.run(host='0.0.0.0', port=HTTP_PORT, loop_forever=loop_forever)
