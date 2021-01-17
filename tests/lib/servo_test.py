from machine import Pin, PWM
servo = PWM(Pin(18), freq=50, duty=50)
from time import sleep_ms

# 38-133
servo.duty(40)
sleep_ms(1000)
for i in range(40, 134, 1):
    print(i)
    servo.duty(i)
    sleep_ms(1)

