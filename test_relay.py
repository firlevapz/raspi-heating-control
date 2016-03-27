#!/usr/bin/python3

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)


relay_pin = 11
GPIO.setup(relay_pin, GPIO.OUT)

GPIO.output(relay_pin, GPIO.HIGH)





