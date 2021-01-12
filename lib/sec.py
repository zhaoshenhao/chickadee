
from utils import singleton
from enc import cipher, encrypt, decrypt
from ubinascii import a2b_base64, b2a_base64, unhexlify
from uhashlib import sha256
from dev import state

# state = 2，是特殊配置模式

def _hash(salt, key, tm):
    h = sha256(salt + key)
    if tm is not None:
        h.update(tm)
    return h.digest()

@singleton
class Sec:
    def __init__(self, dev_sec, hw_pin):
        self.set_dev_sec(dev_sec)
        self.__hw_pin = hw_pin

    def pad_key(self, key):
        l = 16 / len(key) + 1
        k = key * l
        return k[0:16]

    def set_dev_sec(self, dev_sec):
        self.__dev_sec = self.pad_key(dev_sec)

    def check_token(self, token):
        try:
            l = token.split(':')
            if len(l) == 2:
                if state != 2:
                    return False
                h = _hash(l, self.__hw_pin, None)
            elif len(l) == 3:
                h = _hash(l, self.__dev_sec, l[2])
            else:
                return False
            return h == unhexlify(l[1])
        except: #pylint: disable=bare-except
            return False

    def get_cipher(self):
        if state == 0:
            return cipher(self.pad_key(self.__hw_pin))
        return cipher(self.__dev_sec)

    def dec_payload(self, payload):
        '''
        payload in dict: {'p': 'base64-str'}
        注意：
            1. 返回是字符串
            2. 有 Excpetion需要处理
        '''
        p = payload['p']
        pb = bytes(p, 'ascii')
        bs = a2b_base64(pb)
        return self.dec(bs)

    def enc_payload(self, payload):
        '''
        payload是字符串，返回playload：{'p': 'base64-str'}
        '''
        c = self.get_cipher()
        bs = encrypt(c, payload)
        b64s = b2a_base64(bs)
        return {
            'p': b64s.decode('ascii')[:-1]
        }

    def dec(self, data):
        c = self.get_cipher()
        return decrypt(c, data)

    def enc(self, data):
        c = self.get_cipher()
        return encrypt(c, data)
