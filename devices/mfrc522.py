# MRFC522 class
from mfrc_522 import MFRC522
from machine import Pin, SPI
from hw import log

class Mfrc522:
    def __init__(self, sck_pin=18, mosi_pin = 23, miso_pin = 19, sda_pin = 5):
        sck = Pin(sck_pin, Pin.OUT)
        mosi = Pin(mosi_pin, Pin.OUT)
        miso = Pin(miso_pin, Pin.OUT)
        spi = SPI(baudrate=100000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)
        sda = Pin(sda_pin, Pin.OUT)
        self._rdr = MFRC522(spi, sda)
        self._addr = 8

    def get_stat(self):
        try:
            while True:
                uid = ""
                (stat, tag_type) = self._rdr.request(self._rdr.REQIDL)
                if stat == self._rdr.OK:
                    (stat, raw_uid) = self._rdr.anticoll()
                    if stat == self._rdr.OK:
                        uid = ("0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
                        log.info("New card detected")
                        log.info("  - tag type: 0x%02x", tag_type)
                        log.info("  - uid     : %s", uid)
                        return stat, tag_type, raw_uid, uid
        except BaseException as e:
            log.info("Stop getting stat %r", e)

    # Place card before reader to write address 0x08
    def write(self, data):
        log.info("Writing...")
        try:
            while True:
                (stat, _, raw_uid, _) = self.get_stat()
                if stat == self._rdr.OK:
                    if self._rdr.select_tag(raw_uid) == self._rdr.OK:
                        key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
                        if self._rdr.auth(self._rdr.AUTHENT1A, 8, key, raw_uid) == self._rdr.OK:
                            stat = self._rdr.write(self._addr, data)
                            self._rdr.stop_crypto1()
                            if stat == self._rdr.OK:
                                log.info("Data written to card")
                                return True
                            log.error("Failed to write data to card")
                        else:
                            log.error("Authentication error")
                    else:
                        log.error("Failed to select tag")
        except BaseException as e:
            log.info("Stop writing %r", e)
        return False

    def read(self): #NOSONAR
        try:
            while True:
                (stat, tag_type, raw_uid, uid) = self.get_stat()
                if stat == self._rdr.OK:
                    if self._rdr.select_tag(raw_uid) == self._rdr.OK:
                        key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
                        if self._rdr.auth(self._rdr.AUTHENT1A, 8, key, raw_uid) == self._rdr.OK:
                            data = self._rdr.read(self._addr)
                            self._rdr.stop_crypto1()
                            if data is not None:
                                return stat, tag_type, raw_uid, uid, data
                            log.error("Failed to read data to card")
                        else:
                            log.error("Authentication error")
                    else:
                        log.error("Failed to select tag")
        except BaseException as e:
            log.info("Stop reading %r", e)

