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
        else:
            self.ap.active(True)
            self.ap.config(essid = DEVICE_NAME, password = HW_PIN)
            while self.ap.active():
                sleep(1)

    def get_info(self):
        if self.ap.active():
            (ip, _, gw, _) = self.ap.config()
            return {
                'ip': ip,
                'gw': gw
            }
        return None
