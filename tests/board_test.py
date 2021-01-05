from board import Board
import uasyncio as asyncio
import logging
logging._level = logging.DEBUG

#hw.WIFI_CHECK_INTVAL = 3
try:
    d = Board()
    asyncio.run(d.start())
finally:
    asyncio.new_event_loop()

