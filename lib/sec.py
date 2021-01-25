from utils import singleton, random_string, time_stamp
from enc import cipher, encrypt, decrypt
from ubinascii import a2b_base64, b2a_base64
from uhashlib import sha256
from ujson import loads, dumps
from ucryptolib import aes
import dev

# state = 2，是特殊配置模式

def b2a_base64_trimed(bs: bytes):
    b64s = b2a_base64(bs)
    return b64s.decode('ascii')[:-1]

def _hash(salt : str, key : str,  tm : str):
    h = sha256(salt + key)
    if tm is not None:
        h.update(tm)
    return h.digest()

def _pad_key(key : str) -> str:
    l = int(16 / len(key) + 1)
    k = key * l
    return k[0:16]

@singleton
class Sec:
    def __init__(self, dev_sec : str = None, hw_pin : str = None):
        if hw_pin is not None:
            self.__hw_pin = hw_pin
        if dev_sec is not None:
            self.__dev_sec = _pad_key(dev_sec)

    def check_token(self, token : str):
        try:
            l = token.split(':')
            if len(l) == 2:
                if dev.state != 2:
                    return False
                h = _hash(l[0], self.__hw_pin, None)
            elif len(l) == 3:
                h = _hash(l[0], self.__dev_sec, l[2])
            else:
                return False
            return h == a2b_base64(l[1])
        except: #pylint: disable=bare-except
            return False

    def create_token(self, special : bool = False):
        salt = random_string(4)
        if special:
            h = _hash(salt, self.__hw_pin, None)
            return salt + ":" + b2a_base64_trimed(h)
        else:
            tm = str(time_stamp())
            h = _hash(salt, self.__dev_sec, tm)
            return salt + ":" + b2a_base64_trimed(h) + ":" + tm

    def get_cipher(self) -> aes:
        if dev.state == 0:
            return cipher(_pad_key(self.__hw_pin))
        return cipher(self.__dev_sec)

    def dec_payload(self, payload : dict) -> dict:
        if payload is None or len(payload) == 0:
            return None
        else:
            bs = self.dec_payload_str(payload)
            return loads(bs.decode('utf-8'))

    def enc_paylaod(self, payload : dict) -> dict:
        if payload is None:
            s = ''
        else:
            s = dumps(payload)
        return self.enc_payload_str(s)

    def dec_payload_str(self, payload : dict) -> bytes:
        '''
        payload in dict: {'_': 'base64-str'}
        注意：
            1. 返回是字符串
            2. 有 Excpetion需要处理
        '''
        if payload is None or len(payload) == 0:
            return None
        p = payload['_']
        pb = bytes(p, 'ascii')
        bs = a2b_base64(pb)
        return self.dec(bs)

    def enc_payload_str(self, payload : str) -> dict:
        '''
        payload是字符串，返回payload：{'_': 'base64-str'}
        '''
        c = self.get_cipher()
        bs = encrypt(c, payload)
        return {
            '_': b2a_base64_trimed(bs)
        }

    def dec(self, data : bytes) -> bytes:
        c = self.get_cipher()
        return decrypt(c, data)

    def enc(self, data : str) -> bytes:
        c = self.get_cipher()
        return encrypt(c, data)
