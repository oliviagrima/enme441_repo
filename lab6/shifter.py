# shifter.py
import RPi.GPIO as GPIO
import time

class Shifter:
    def __init__(self, serialPin, clockPin, latchPin):
        self.serialPin = serialPin
        self.clockPin = clockPin
        self.latchPin = latchPin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.serialPin, GPIO.OUT)
        GPIO.setup(self.clockPin, GPIO.OUT, initial=0)
        GPIO.setup(self.latchPin, GPIO.OUT, initial=0)

    def __ping(self, pin):  # método privado
        GPIO.output(pin, 1)
        time.sleep(0)
        GPIO.output(pin, 0)

    def shiftByte(self, byte):  # método público
        for i in range(8):
            GPIO.output(self.serialPin, byte & (1 << i))
            self.__ping(self.clockPin)
        self.__ping(self.latchPin)

from shifter import Shifter
import time

s = Shifter(23, 25, 24)  # serialPin, clockPin, latchPin

try:
    while True:
        for i in range(2**8):
            s.shiftByte(i)
            time.sleep(0.5)
except KeyboardInterrupt:
    GPIO.cleanup()
