from micropython import const
from ucryptolib import aes

MODE_ECB = const(1)
MODE_CBC = const(2)
MODE_CTR = const(6)
BLOCK_SIZE = const(16)

def pad(data_to_pad, block_size = BLOCK_SIZE):
    padding_len = block_size-len(data_to_pad)%block_size
    padding = chr(padding_len)*padding_len
    return data_to_pad + padding

def unpad(padded_data, block_size = BLOCK_SIZE):
    pdata_len = len(padded_data)
    if pdata_len % block_size:
        raise ValueError("Input data is not padded")
    padding_len = padded_data[-1]
    if padding_len<1 or padding_len>min(block_size, pdata_len) or padded_data[-padding_len:]!=bytes(chr(padding_len)*padding_len, 'ascii'):
        raise ValueError("Padding is incorrect.")
    return padded_data[:-padding_len]

def encrypt(c, plaintext, bsize = BLOCK_SIZE):
    if c is None or plaintext is None:
        return None
    return c.encrypt(pad(plaintext, bsize))

def decrypt(c, data):
    if c is None or data is None:
        return None
    return unpad(c.decrypt(data))

def cipher(key, mode = MODE_ECB):
    bs = bytes(key, 'ascii')
    return aes(bs, mode)
