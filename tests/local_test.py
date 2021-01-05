# Write your code here :-)
# test dir op
#import os
#print(os.getcwd())
#for i in os.ilistdir("/"):
#    print(i)
#os.remove("/lib/micropython.py")
#os.remove("/lib/uos.py")
#os.rmdir("/lib")

# reboot
import machine
machine.reset()

# test relay
'''
from relay import Relay
from time import sleep

# ESP32 GPIO 22
relay = Relay(22)
print("Current status: ", relay.get_state())
sleep(1)
print("Switch on")
relay.on()
sleep(5)
print("Switch off")
relay.off()
'''
# test wifi
#from wifi import Wifi
#wifi = Wifi(20)
#wifi.connect()
#print(wifi.is_connected())
#def demo():
#    wifi = Wifi(20)
#    wifi.connect()

#if __name__ == "__main__":
#    demo()
