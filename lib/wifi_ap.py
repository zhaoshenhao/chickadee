from time import sleep
from network import WLAN, AP_IF
from utils import singleton
from hw import DEVICE_NAME, HW_PIN

@singleton
class WifiAp:
    def __init__(self):
        self.ap = WLAN(AP_IF)

    def start_ap(self):
        if self.ap.active():
            return
        self.ap.active(True)
        self.ap.config(essid = DEVICE_NAME, password = HW_PIN)
        while not self.ap.active():
            sleep(1)

    def stop_ap(self):
        if self.ap.active():
            self.ap.active(False)

    def get_info(self):
        if self.ap.active():
            (ip, _, gw, _) = self.ap.ifconfig()
            return {
                'ip': ip,
                'gw': gw
            }
        return None
