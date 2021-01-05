# Utilities
import time
import machine
import urandom
import ustruct as struct

'''
Check if the string is empty (None, empty or with space only)
'''
def is_str_empty(str):
    return str == None or str.isspace() or str == ''

'''
The singleton decorator. Usage:
@singleton
class MyClass
'''
def singleton(cls):
    instance = None
    def getinstance(*args, **kwargs):
        nonlocal instance
        if instance is None:
            instance = cls(*args, **kwargs)
        return instance
    return getinstance

'''
The functor decorator
Usage:
@functor
class MyClass
...
    def __call__(self, arg):
'''
def functor(cls):
    instance = None
    def getinstance(*args, **kwargs):
        nonlocal instance
        if instance is None:
            instance = cls(*args, **kwargs)
            return instance
        return instance(*args, **kwargs)
    return getinstance

'''
Generate random string
'''
def random_string(length=8):
    #Generate a random string of fixed length
    _randomstring = ''
    x = 0
    #add random seed seconds of localtime
    urandom.seed(time.localtime()[5])
    while x < length:
        _randomstring = _randomstring + urandom.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890')
        x += 1
    return _randomstring

def set_gc():
    from gc import threshold, mem_free, mem_alloc
    threshold(mem_free() // 4 + mem_alloc())

