from bluetooth import UUID, BLE
from ble_advertising import advertising_payload
from micropython import const
from hw import log
from json import loads, dumps
from op import AUTH_ERR, TOKEN, result
from uasyncio import create_task, sleep
from consumer import Consumer

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

_UART_UUID = UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
    UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_NOTIFY,
)
_UART_RX = (
    UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_WRITE,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)

# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_COMPUTER = const(128)
AUTH_FAILED_COUNT = 10

class BLEUART(Consumer):
    def __init__(self, opc, name="ybb", rxbuf=1024):
        self._ble = BLE()
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._tx_handle, self._rx_handle),) = self._ble.gatts_register_services((_UART_SERVICE,))
        # Increase the size of the rx buffer and enable append mode.
        self._ble.gatts_set_buffer(self._rx_handle, rxbuf, True)
        self._connections = {}
        self._rx_buffer = bytearray()
        self._opc = opc
        # Optionally add services=[_UART_UUID], but this is likely to make the payload too large.
        self._payload = advertising_payload(name=name[:8], appearance=_ADV_APPEARANCE_GENERIC_COMPUTER)
        self._advertise()

    def _parse(self):
        try:
            bs = self.read()
            log.debug("Read data: %s", bs)
            d = bs.decode().strip()
            json = loads(d)
            if TOKEN not in json:
                return None, json
            return json[TOKEN], json
        except Exception as e:
            log.debug("Invalid request: %s" % e)
            return None, None
    
    def send(self, r):
        try:
            if not self.is_authed():
                log.debug("No authenticated central")
                return
            self.write(dumps(r))
        except Exception as e:
            log.debug("Send failed: %r" % r)

    def _handle(self):
        t, d = self._parse()
        tm = self._opc.tm_auth(t)
        if tm is not None:
            self.send(tm)
        elif not self._opc.auth(t):
            self.send(AUTH_ERR)
        else:
            print("Set auth")
            self._set_auth()
            create_task(self._call(d))

    def _set_auth(self):
        for conn_handle in self._connections:
            self._connections[conn_handle] = -1

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections[conn_handle] = 0
            log.debug("New connection")
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            log.debug("Disconnected")
            if conn_handle in self._connections:
                del self._connections[conn_handle]
            # Start advertising again to allow a new connection.
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if conn_handle in self._connections and value_handle == self._rx_handle:
                self._rx_buffer += self._ble.gatts_read(self._rx_handle)
                self._handle()

    def any(self):
        return len(self._rx_buffer)

    def read(self, sz=None):
        if not sz:
            sz = len(self._rx_buffer)
        result = self._rx_buffer[0:sz]
        self._rx_buffer = self._rx_buffer[sz:]
        return result

    def write(self, data, authed = False):
        for conn_handle in self._connections:
            if not authed or self._connections[conn_handle] < 0:
                log.debug("Send data: %s", data)
                self._ble.gatts_notify(conn_handle, self._tx_handle, data)

    def close(self):
        for conn_handle in self._connections:
            self._ble.gap_disconnect(conn_handle)
        self._connections.clear()

    def disconnect(self, conn_handle):
        if conn_handle in self._connections:
            self._ble.gap_disconnect(conn_handle)

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)
        log.info("Advertised", )

    def is_authed(self):
        for conn_handle in self._connections:
            if self._connections[conn_handle] < 0:
                return True
        return False

    def check_auth(self):
        for conn_handle in self._connections:
            if self._connections[conn_handle] >= 0:
                self._connections[conn_handle] = self._connections[conn_handle] + 1
                if self._connections[conn_handle] > AUTH_FAILED_COUNT:
                    log.info("Connect is not authenticated: %d, disconnected.", conn_handle)
                    self.disconnect(conn_handle)

    async def _call(self, data):
        try:
            r = await self._opc.op_request(data, False)
            self.send(r)
        except Exception as e:
            msg = "Call failed %r" % e
            log.debug(msg)
            self.send(result(500, msg))

    async def monitor(self):
        '''
        清理非法连接
        '''
        log.debug("BLE connection monitor")
        while True:
            try:
                sleep(1)
                self.check_auth()
            except: # NOSONAR
                pass

    async def consume(self, data):
        self.send(data)
        sleep(0)
