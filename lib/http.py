import tinyweb

from utils import singleton
from hw import log, HTTP_PORT

@singleton
class Http:
    def __init__(self):
        self.__app = tinyweb.webserver()

    def run(self):
        self.__app.run(host='0.0.0.0', port=HTTP_PORT, loop_forever=False)

@app.catchall()
async def index(request, response):
    req.me
    # Start HTTP response with content-type text/html
    await response.start_html()
    # Send actual HTML page
    await response.send('<html><body><h1>Hello, world! (<a href="/table">table</a>)</h1></html>\n')
