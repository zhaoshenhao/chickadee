from micropython import const
from ucryptolib import aes

MODE_ECB = const(1)
MODE_CBC = const(2)
MODE_CTR = const(6)
BLOCK_SIZE = const(16)

def pad(data_to_pad : str, block_size : int = BLOCK_SIZE) -> bytes:
    padding_len = block_size-len(data_to_pad)%block_size
    padding = chr(padding_len)*padding_len
    return bytes(data_to_pad + padding, 'utf-8')

def unpad(padded_data : bytes, block_size : int = BLOCK_SIZE) -> bytes:
    pdata_len = len(padded_data)
    if pdata_len % block_size:
        raise ValueError("Input data is not padded")
    padding_len = padded_data[-1]
    if padding_len<1 or padding_len>min(block_size, pdata_len) or padded_data[-padding_len:]!=bytes(chr(padding_len)*padding_len, 'ascii'):
        raise ValueError("Padding is incorrect.")
    return padded_data[:-padding_len]

def encrypt(c : aes, plaintext : str, bsize : int = BLOCK_SIZE) -> bytes:
    if c is None or plaintext is None:
        return None
    return c.encrypt(pad(plaintext, bsize))

def decrypt(c: aes, data: bytes) -> bytes:
    if c is None or data is None:
        return None
    return unpad(c.decrypt(data))

def cipher(key: str, mode : int = MODE_ECB) -> aes:
    bs = bytes(key, 'ascii')
    return aes(bs, mode)
