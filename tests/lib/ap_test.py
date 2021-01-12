import network
import gc

gc.collect()

ssid = 'ybb'
password = '123456789'

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid, password=password)

while ap.active() == False:
      pass

print('Connection successful')
print(ap.ifconfig())