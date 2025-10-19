import RPi.GPIO as GPIO
import time

s1_pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(s1_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    while True:
        print(GPIO.input(s1_pin))
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
