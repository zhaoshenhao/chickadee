# ULN2003 en 28BYJ-48 5v Stepper Motor for use with ESP8266 and Wemos D1.
# Author: Michiel Erasmus, adapted from various sources
# Version: 0.1  20200522

import machine
import micropython
import time
from micropython import const; _X=const(1)  # https://github.com/IDWizard/uln2003
import micropython
import network
import esp
esp.osdebug(None)
import gc
gc.collect()

LOW = 0
HIGH = 1
FULL_ROTATION = int(4075.7728395061727 / 8) # http://www.jangeox.be/2013/10/stepper-motor-28byj-48_25.html

MODE_ACHTERUIT = [
    [LOW, LOW, LOW, HIGH],
    [LOW, LOW, HIGH, HIGH],
    [LOW, LOW, HIGH, LOW],
    [LOW, HIGH, HIGH, LOW],
    [LOW, HIGH, LOW, LOW],
    [HIGH, HIGH, LOW, LOW],
    [HIGH, LOW, LOW, LOW],
    [HIGH, LOW, LOW, HIGH],
]

MODE_VOORUIT = [
 [HIGH, LOW, HIGH, LOW],
 [LOW, HIGH, HIGH, LOW],
 [LOW, HIGH, LOW, HIGH],
 [HIGH, LOW, LOW, HIGH]
]

class Command():
    """Tell a stepper to move X many steps in direction"""
    def __init__(self, stepper, steps, direction=1):
        self.stepper = stepper
        self.steps = steps
        self.direction = direction

class Driver():
    """Drive a set of motors, each with their own commands"""

    @staticmethod
    def run(commands):
        """Takes a list of commands and interleaves their step calls"""
        
        # Work out total steps to take
        max_steps = int(sum([c.steps for c in commands]))

        count = 0
        while(count != max_steps):
            for command in commands:
                # we want to interleave the commands
                if(command.steps > 0):
                    command.stepper.step(1, command.direction)
                    command.steps -= 1
                    count += 1


class Stepper():
    def __init__(self, mode, in1, in2, in3, in4, delay=2):
        self.mode = mode
        self.in1 = machine.Pin(in1, machine.Pin.OUT)
        self.in2 = machine.Pin(in2, machine.Pin.OUT)
        self.in3 = machine.Pin(in3, machine.Pin.OUT)
        self.in4 = machine.Pin(in4, machine.Pin.OUT)
        self.delay = delay  # Recommend 10+ for FULL_STEP, 1 is OK for HALF_STEP
        self.LOW = 0
        self.HIGH = 1

        self.reset()


    def step(self, count, direction=1):
        """Rotate count steps. direction = -1 means backwards"""
        for x in range(count):
            for bit in self.mode[::direction]:
                self.in1.value(bit[0]) 
                self.in2.value(bit[1]) 
                self.in3.value(bit[2]) 
                self.in4.value(bit[3]) 
                time.sleep(self.delay)
        self.reset()

    def reset(self):
        self.in1.value(0)
        self.in2.value(0)
        self.in3.value(0)
        self.in4.value(0)

    def testAllesAan(self, waarde):
        self.in1.value(waarde)
        self.in2.value(waarde)
        self.in3.value(waarde)
        self.in4.value(waarde)
    
