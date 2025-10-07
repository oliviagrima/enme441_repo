import time
import RPi.GPIO as GPIO
import math

GPIO.setmode(GPIO.BCM) 
p = [18, 15, 14, 2, 3, 4, 17, 27, 22, 23]

for pin in p:
    GPIO.setup(pin, GPIO.OUT)

pwms = []
for pin in p:
    pwm = GPIO.PWM(pin, 500)
    pwm.start(0) # start with 0% duty cycle
    pwms.append(pwm)

f = 0.2 # frequency (Hz)
update_interval = 0.01

start_time = time.time()

try:
    while True:
        t = time.time() - start_time

        for i in range (10):
            phi = (math.pi / 11) * i
            B = (math.sin(2 * math.pi * f * t - phi)) ** 2
            dc = B * 100
            pwms[i].ChangeDutyCycle(dc)

        loop_start = time.time()
        while (time.time() - loop_start) < update_interval:
            pass

except KeyboardInterrupt: # stop gracefully on ctrl-C
    print('\nExiting')
for pwm in pwms:
    pwm.stop()
GPIO.cleanup()