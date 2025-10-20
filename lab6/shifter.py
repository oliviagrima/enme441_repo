"""
Olivia Grima
ENME441 - Lab 6
"""

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

    def __ping(self, pin):  # private method 
        GPIO.output(pin, 1)
        time.sleep(0)
        GPIO.output(pin, 0)

    def shiftByte(self, byte):  # public method
        for i in range(8):
            GPIO.output(self.serialPin, byte & (1 << i))
            self.__ping(self.clockPin)
        self.__ping(self.latchPin)