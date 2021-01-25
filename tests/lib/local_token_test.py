from hashlib import sha256
from time import time
import base64

def _hash(salt : str, key : str,  tm : str):
    h = sha256(salt + key)
    if tm is not None:
        h.update(tm)
    return h.digest()

s = b'abcd'
pin = b'12345678'
skey = b'kB8nd4GLzz2ACrWZhCLiq4ImGjDpRkiz'
h1 = _hash(s, pin, None)
t1 = s + b":" + base64.b64encode(h1)
stm = bytes(str(int(time())), 'utf-8')
h2 = _hash(s, skey, stm)
t2 = s + b":" + base64.b64encode(h2) + b":" + stm

print("Token:")
print("Speical token: ", t1)
print("Normal token: ", t2)
