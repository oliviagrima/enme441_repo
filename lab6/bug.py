# bug.py
from shifter import Shifter
import time
import random
import threading
import RPi.GPIO as GPIO

class Bug:
    def __init__(self, timestep=0.1, x=3, isWrapOn=False):
        self.timestep = timestep
        self.x = x
        self.isWrapOn = isWrapOn
        self.__shifter = Shifter(serialPin=23, clockPin=25, latchPin=24)
        self.__running = False
        self.__thread = None

    # Método privado que hace el movimiento
    def __move(self):
        while self.__running:
            byte = 1 << self.x
            self.__shifter.shiftByte(byte)

            move = random.choice([-1, 1])
            self.x += move

            if self.isWrapOn:
                self.x %= 8  # envuelve de 0 a 7
            else:
                if self.x < 0:
                    self.x = 0
                elif self.x > 7:
                    self.x = 7

            time.sleep(self.timestep)

    # Método público para iniciar el bug
    def start(self):
        if not self.__running:
            self.__running = True
            self.__thread = threading.Thread(target=self.__move)
            self.__thread.start()

    # Método público para detener el bug
    def stop(self):
        self.__running = False
        if self.__thread:
            self.__thread.join()
        self.__shifter.shiftByte(0)  # apaga todos los LEDs
        GPIO.cleanup()
