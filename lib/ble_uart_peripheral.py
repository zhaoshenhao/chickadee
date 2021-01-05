# This example demonstrates a peripheral implementing the Nordic UART Service (NUS).

import bluetooth
from ble_advertising import advertising_payload
from micropython import const
from utils import singleton
from hw import DEVICE_NAME
import logging

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    bluetooth.FLAG_WRITE | bluetooth.FLAG_WRITE_NO_RESPONSE,
)
_UART_TX = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)

AUTH_FAILED_COUNT = 20 # times
BLE_TASK_INTERVAL = 1000 # ms

#https://www.bluetooth.com/wp-content/uploads/Sitecore-Media-Library/Gatt/Xml/Characteristics/org.bluetooth.characteristic.gap.appearance.xml
BLE_APPEARANCE_UNKNOWN = const(0)
BLE_APPEARANCE_GENERIC_PHONE = const(64)
BLE_APPEARANCE_GENERIC_COMPUTER = const(128)
BLE_APPEARANCE_GENERIC_WATCH = const(192)
BLE_APPEARANCE_WATCH_SPORTS_WATCH = const(193)
BLE_APPEARANCE_GENERIC_CLOCK = const(256)
BLE_APPEARANCE_GENERIC_DISPLAY = const(320)
BLE_APPEARANCE_GENERIC_REMOTE_CONTROL = const(384)
BLE_APPEARANCE_GENERIC_EYE_GLASSES = const(448)
BLE_APPEARANCE_GENERIC_TAG = const(512)
BLE_APPEARANCE_GENERIC_KEYRING = const(576)
BLE_APPEARANCE_GENERIC_MEDIA_PLAYER = const(640)
BLE_APPEARANCE_GENERIC_BARCODE_SCANNER = const(704)
BLE_APPEARANCE_GENERIC_THERMOMETER = const(768)
BLE_APPEARANCE_THERMOMETER_EAR = const(769)

@singleton
class BleUart:
    def __init__(self, name="ybb-home", rxbuf=1025, appearance = BLE_APPEARANCE_UNKNOWN):
        self._ble = bluetooth.BLE()
        self._log = logging.getLogger("ble")
        self._name = name
        self._appearance = appearance
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._tx_handle, self._rx_handle),) = self._ble.gatts_register_services((_UART_SERVICE,))
        # Increase the size of the rx buffer and enable append mode.
        self._ble.gatts_set_buffer(self._rx_handle, rxbuf, True)
        self._connections = {} # key: the conn_handle, value: the auth failed count, -1: succ, 0-n, failed count
        self._rx_buffer = bytearray()
        self._handler = None
        # Optionally add services=[_UART_UUID], but this is likely to make the payload too large.
        self._payload = advertising_payload(name=name, appearance=self._appearance)
        self._advertise()

    def irq(self, handler):
        self._handler = handler

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._log.info("New connection: %s", conn_handle)
            self._connections[conn_handle] = 0
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._log.info("Disconnected from remote: %s", conn_handle)
            if conn_handle in self._connections:
                del self._connections[conn_handle]
            # Start advertising again to allow a new connection.
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if conn_handle in self._connections and value_handle == self._rx_handle:
                self._rx_buffer += self._ble.gatts_read(self._rx_handle)
                if self._handler:
                    self._handler()

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
                self._log.info("Send data: %s", data) # TODO remove
                self._ble.gatts_notify(conn_handle, self._tx_handle, data)

    def close(self):
        for conn_handle in self._connections:
            self._ble.gap_disconnect(conn_handle)
        self._connections.clear()

    def disconnect(self, conn_handle):
        if conn_handle in self._connections:
            self._ble.gap_disconnect(conn_handle)

    def _advertise(self, interval_us=500000):
        self._log.info("Starting advertising...")
        self._ble.gap_advertise(interval_us, adv_data=self._payload)
        self._log.info("Bluetooth advertised")
        self._log.info("uuid: %s", _UART_UUID)
        self._log.info("uuid_rx: %s", _UART_RX)
        self._log.info("uuid_tx: %s", _UART_TX)
        self._log.info("device_type: %d", self._appearance)
        self._log.info("name: %s", self._name)

    def check_auth(self):
        print("check auth")
        for conn_handle in self._connections:
            self._log.info("check auth: %d", conn_handle)
            if self._connections[conn_handle] >= 0:
                self._connections[conn_handle] = self._connections[conn_handle] + 1
                if self._connections[conn_handle] > AUTH_FAILED_COUNT:
                    self._log.info("Connect is not authenticated: %d, disconnected.", conn_handle)
                    self.disconnect(conn_handle)

def demo():
    import time
    mname = DEVICE_NAME
    uart = BleUart(name = mname, appearance = BLE_APPEARANCE_GENERIC_THERMOMETER)

    def on_rx():
        print("rx: ", uart.read().decode().strip())

    uart.irq(handler=on_rx)
    nums = [4, 8, 15, 16, 23, 42]
    i = 0

    try:
        while True:
            uart.check_auth()
            uart.write(str(nums[i]) + "\n")
            i = (i + 1) % len(nums)
            time.sleep_ms(1000)
    except KeyboardInterrupt:
        pass

    uart.close()

if __name__ == "__main__":
    demo()
