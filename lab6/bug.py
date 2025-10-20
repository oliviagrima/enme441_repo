"""
Olivia Grima
ENME441 - Lab 6
"""

from shifter import Shifter
import time
import random
import threading
import RPi.GPIO as GPIO

DEBOUNCE_TIME = 0.2 

class Bug:
    def __init__(self, timestep=0.1, x=3, isWrapOn=False):
        self.timestep = timestep
        self.x = x
        self.isWrapOn = isWrapOn
        self.__shifter = Shifter(serialPin=23, clockPin=25, latchPin=24)
        self.__running = False
        self.__thread = None

    def __move(self):
        while self.__running:
            byte = 1 << self.x
            self.__shifter.shiftByte(byte)

            move = random.choice([-1, 1])
            self.x += move

            if self.isWrapOn:
                self.x %= 8
            else:
                self.x = max(0, min(7, self.x))

            time.sleep(self.timestep)

    def start(self):
        if not self.__running:
            self.__running = True
            self.__thread = threading.Thread(target=self.__move)
            self.__thread.start()

    def stop(self):
        if self.__running:
            self.__running = False
            self.__thread.join()
        self.__shifter.shiftByte(0)


if __name__ == "__main__":
    # switches pins
    s1_pin = 17  # turns bug on/off
    s2_pin = 27  # changes wrapping
    s3_pin = 22  # speeds up

    GPIO.setmode(GPIO.BCM)
    # Configuration with internal pull-up (switch connected to GND)
    GPIO.setup(s1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(s2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(s3_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    b = Bug()
    prev_s2 = not GPIO.input(s2_pin)
    prev_s3 = not GPIO.input(s3_pin)

    try:
        while True:
            # switches connected to GND, so invert reading
            s1 = not GPIO.input(s1_pin)
            s2 = not GPIO.input(s2_pin)
            s3 = not GPIO.input(s3_pin)

            # Turns bug on/off
            if s1:
                b.start()
            else:
                b.stop()

            # Change wrapping with debounce
            if s2 != prev_s2 and s2:
                b.isWrapOn = not b.isWrapOn
                prev_s2 = s2
                time.sleep(DEBOUNCE_TIME)  # debounce

            # Adjust speed with debounce
            if s3 != prev_s3:
                if s3:
                    b.timestep = 0.1 / 3
                else:
                    b.timestep = 0.1
                prev_s3 = s3
                time.sleep(DEBOUNCE_TIME)

            time.sleep(0.01)

    except KeyboardInterrupt:
        b.stop()
        GPIO.cleanup()
