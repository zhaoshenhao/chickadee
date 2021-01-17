from time import sleep
from wifi_ap import WifiAp

ap = WifiAp()

print("AP active = ", ap.ap.active())
print("Start ap")
ap.start_ap()
print("AP active = ", ap.ap.active())
print("AP status: %r" % ap.get_info())
sleep(20)
print("Stop ap")
ap.stop_ap()
print("AP active = ", ap.ap.active())
