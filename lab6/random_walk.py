from shifter import Shifter
import time
import random
import RPi.GPIO as GPIO


s = Shifter(serialPin=23, clockPin=25, latchPin=24)
position = 3
timestep = 0.05

try:
    while True:
        byte = 1 << position
        s.shiftByte(byte)

        move = random.choice([-1, 1])
        position += move

        if position < 0:
            position = 0
        elif position > 7:
            position = 7

        time.sleep(timestep)

except KeyboardInterrupt:
    s.shiftByte(0)
    GPIO.cleanup()
