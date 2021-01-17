from umqtt.simple import MQTTClient

# Test reception e.g. with:
# mosquitto_sub -t foo_topic
host = b"47.102.211.32"
port = 8883
user = b"test1"
password = b"mqtttest1"
topic = b"chickadee/sensors"
ssl_param = {'ca_certs': 'ca.pem'}


c = MQTTClient("umqtt_client", host, port, user, password, 0, True)
c.connect()
c.publish(topic, b"hello")
c.disconnect()

