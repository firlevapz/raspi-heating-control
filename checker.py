#!/usr/bin/python3
import os
import subprocess
import time
import threading
import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor

import django
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "heatingcontrol.settings")
django.setup()

from heatingcontrol.models import Config, Sensor, Temperature, Timestamp

oven_pin = 11

config_reload = 10 # seconds how often reload the config

cleanup_wait = 3600*24 # cleanup once a day
temp_read_wait = 60*10  # each 10 minutes check for devices
oven_check_wait = 60 # check for oven status each minute

stop_threads = threading.Event()    # threading event to stop all threads

# GPIO setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(oven_pin, GPIO.OUT)


def read_temperature():
    while not stop_threads.isSet():
        sensors = Sensor.objects.all()
        timestamp = Timestamp.objects.create()

        for s in sensors:
            sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, s.w1_id)
            temp = sensor.get_temperature()
            while temp == 85:
                temp = sensor.get_temperature()
                time.sleep(1)
            new_temp = Temperature.objects.create(sensor=s, value=temp, created=timestamp)
        time.sleep(temp_read_wait)


def check_oven():
    while not stop_threads.isSet():
        oven, _ = Config.objects.get_or_create(name__exact='ofen')

        GPIO.output(oven_pin, 0) if oven.enabled else GPIO.output(oven_pin, 1)

        time.sleep(oven_check_wait)


def cleanup():
    while not stop_threads.isSet():
        oldest = timezone.now() - timezone.timedelta(days=30)
        oldest_timestamps = Timestamp.objects.filter(timestamp__lt=oldest)
        oldest_timestamps.delete()

        time.sleep(cleanup_wait)


if __name__ == '__main__':
    oven, _ = Config.objects.get_or_create(name__exact='ofen')
    oven.enabled = False
    oven.save()

    temp_thread = threading.Thread(target=read_temperature)
    temp_thread.daemon = True
    temp_thread.start()

    relay_thread = threading.Thread(target=check_oven)
    relay_thread.daemon = True
    relay_thread.start()

    cleanup_thread = threading.Thread(target=cleanup)
    cleanup_thread.daemon = True
    cleanup_thread.start()

    try:
        while True:
            # Load configuration-settings from DB
            for c in Config.objects.filter(enabled=True):
                try:
                    locals()[c.name] = float(c.value)
                except:
                    locals()[c.name] = c.value
                    
            time.sleep(config_reload)
    except (KeyboardInterrupt, SystemExit):
        print('Interrupt received, cleaning up...')

    GPIO.cleanup()
