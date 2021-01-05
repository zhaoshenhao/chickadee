'''
import uasyncio as asyncio
from controller import Controller

def set_global_exception():
    def handle_exception(loop, context):
        import sys
        sys.print_exception(context["exception"])
        sys.exit()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)

async def main():
    set_global_exception()  # Debug aid
    dev = Controller()
    asyncio.run(dev.start())

    await device.start()

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()  # Clear retained state
'''