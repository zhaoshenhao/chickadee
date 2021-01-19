from machine import Pin
from primitives.pushbutton import Pushbutton
from uasyncio import sleep, run

def __long_press():
    print("Long")

def __double_press():
    print("Double")

async def __setup_button():
    pin = Pin(32,Pin.IN,Pin.PULL_UP)
    pb = Pushbutton(pin)
    pb.long_func(__long_press)
    pb.double_func(__double_press)

async def my_app():
    __setup_button()
    await sleep(120)  # Dummy

run(my_app())
