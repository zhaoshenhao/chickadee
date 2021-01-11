from mqtt_lib import MQTTClient
import hw
import time
from wifi_sync import WifiSync

SENSOR_TOPIC = "chickadee/sensors"
CMD_TOPIC = "c/" + hw.DEVICE_NAME
HOST = '192.168.0.102'
PORT = 1883
USER = 'test'
PSWD = 'test'

def puback_cb(msg_id):
    print('PUBACK ID = %r' % msg_id)

def suback_cb(msg_id, qos):
    print('SUBACK ID = %r, Accepted QOS = %r' % (msg_id, qos))
  
def con_cb(connected):
    print("Connected. Subscribing now")
    if connected:
      client.subscribe(CMD_TOPIC)

def msg_cb(topic, pay):
    print('Received %s: %s' % (topic.decode("utf-8"), pay.decode("utf-8")))

###### Main
wifi = WifiSync('ybb-home')
wifi.connect()

client = MQTTClient(HOST, port=PORT)

client.set_connected_callback(con_cb)
client.set_puback_callback(puback_cb)
client.set_suback_callback(suback_cb)
client.set_message_callback(msg_cb)

client.connect(hw.DEVICE_NAME, user = USER, password = PSWD)

print("ID: " + hw.DEVICE_NAME)

cnt = 0
while True:
    cnt = cnt + 1
    if cnt == 10:
        wifi.disconnect()
    if cnt == 20:
        wifi.connect(True)
    if client.isconnected():
        try:
            pub_id = client.publish(SENSOR_TOPIC, 'payload' + str(cnt), False, qos = 1)
        except Exception as e:
            print(e)
    time.sleep_ms(2000)

