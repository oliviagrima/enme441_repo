import time
import RPi.GPIO as GPIO
import math

GPIO.setmode(GPIO.BCM) 
p1 = 18
p2 = 13
GPIO.setup(p1, GPIO.OUT)
GPIO.setup(p2, GPIO.OUT)

pwm1 = GPIO.PWM(p1, 500)
pwm1.start(0) # start with 0% duty cycle

pwm2 = GPIO.PWM(p2, 500)
pwm2.start(0) # start with 0% duty cycle

f = 0.2 # frequency (Hz)
update_interval = 0.01

start_time = time.time()

try:
    while True:
        t = time.time() - start_time

        B1 = (math.sin(2 * math.pi * f * t)) ** 2
        dc1 = B1 * 100
        pwm1.ChangeDutyCycle(dc1)

        B2 = (math.sin(2 * math.pi * f * t - (math.pi/11))) ** 2
        dc2 = B2 * 100
        pwm2.ChangeDutyCycle(dc2)

        loop_start = time.time()
        while (time.time() - loop_start) < update_interval:
            pass

except KeyboardInterrupt: # stop gracefully on ctrl-C
    print('\nExiting')
pwm1.stop()
pwm2.stop()
GPIO.cleanup()