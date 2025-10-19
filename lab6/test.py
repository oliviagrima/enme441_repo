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


# Bloque ejecutable para controlar el Bug con switches
if __name__ == "__main__":
    # Pines de los switches
    s1_pin = 17  # enciende/apaga Bug
    s2_pin = 27  # cambia wrapping
    s3_pin = 22  # aumenta velocidad 3x

    # Configurar pines con pull-up interno porque los switches van a GND
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(s1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(s2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(s3_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    b = Bug()
    prev_s2 = GPIO.input(s2_pin)

    try:
        while True:
            # Lectura de switches (invertida porque con pull-up)
            s1 = not GPIO.input(s1_pin)
            s2 = not GPIO.input(s2_pin)
            s3 = not GPIO.input(s3_pin)

            # Encender/apagar Bug
            if s1:
                b.start()
            else:
                b.stop()

            # Cambiar wrapping si s2 cambia de estado
            if s2 != prev_s2:
                b.isWrapOn = not b.isWrapOn
                prev_s2 = s2

            # Ajustar velocidad con s3
            if s3:
                b.timestep = 0.1 / 3
            else:
                b.timestep = 0.1

            time.sleep(0.01)

    except KeyboardInterrupt:
        b.stop()
        GPIO.cleanup()
