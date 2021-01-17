# Utilities
from gc import threshold, mem_free, mem_alloc #pylint: disable=no-name-in-module
from time import time, localtime
from urandom import seed, choice

def is_str_empty(str1):
    return str1 is None or str1.isspace() or str1 == ''

def singleton(cls):
    instance = None
    def getinstance(*args, **kwargs):
        nonlocal instance
        if instance is None:
            instance = cls(*args, **kwargs)
        return instance
    return getinstance

def functor(cls):
    instance = None
    def getinstance(*args, **kwargs):
        nonlocal instance
        if instance is None:
            instance = cls(*args, **kwargs)
            return instance
        return instance(*args, **kwargs)
    return getinstance

def random_string(length=8):
    #Generate a random string of fixed length
    _randomstring = ''
    x = 0
    #add random seed seconds of localtime
    seed(localtime()[5])
    while x < length:
        _randomstring = _randomstring + choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890')
        x += 1
    return _randomstring

def set_gc():
    threshold(mem_free() // 4 + mem_alloc())

def delayed_task(sec, func, tup_args, is_coro = False):
    from uasyncio import sleep_ms, create_task
    async def __task(sec, func, tup_args):
        await sleep_ms(sec)
        func(tup_args)

    async def __coro_task(sec, func, tup_args):
        await sleep_ms(sec)
        await func(tup_args)

    if is_coro:
        create_task(__coro_task(sec, func, tup_args))
    else:
        create_task(__task(sec, func, tup_args))

def time_stamp():
    return 946684800 + time()
