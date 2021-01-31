from machine import Pin, freq
from nec_ir import *
import uasyncio as asyncio

errors = {BADSTART : 'Invalid start pulse', BADBLOCK : 'Error: bad block',
          BADREP : 'Error: repeat', OVERRUN : 'Error: overrun',
          BADDATA : 'Error: invalid data', BADADDR : 'Error: invalid address'}

def cb(data, addr):
    if data == REPEAT:
        print('Repeat')
    elif data >= 0:
        print(hex(data), hex(addr))
    else:
        print('{} Address: {}'.format(errors[data], hex(addr)))

def test():
    print('Test for IR receiver. Assumes NEC protocol.')
    print('ctrl-c to stop.')
    p = Pin(22, Pin.IN)
    ir = NEC_IR(p, cb, True)  # Assume r/c uses extended addressing
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        asyncio.new_event_loop()  # Still need ctrl-d because of interrupt vector

test()
