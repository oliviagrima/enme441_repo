import time
import RPi.GPIO as GPIO
import math

GPIO.setmode(GPIO.BCM) 
p = 18 # pin number
GPIO.setup(p, GPIO.OUT)

pwm = GPIO.PWM(p, 500)
pwm.start(0) # start with 0% duty cycle

f = 0.2 # frequency (Hz)
update_interval = 0.01

start_time = time.time()

try:
    while True:
        t = time.time() - start_time
        B = (math.sin(2 * math.pi * f * t)) ** 2
        dc = B * 100
        pwm.ChangeDutyCycle(dc)
        loop_start = time.time()
        while (time.time() - loop_start) < update_interval:
            pass

except KeyboardInterrupt: # stop gracefully on ctrl-C
    print('\nExiting')
    pwm.stop()
    GPIO.cleanup()