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

check_pin = 7   # GPIO-Pin nr for heating control

config_reload = 10 # seconds how often reload the config

cleanup_wait = 3600*24 # cleanup once a day
temp_read_wait = 60*10  # each 10 minutes check for devices

stop_threads = threading.Event()    # threading event to stop all threads


def read_temperature():
    while not stop_threads.isSet():
        sensors = Sensor.objects.all()
        timestamp = Timestamp.objects.create()

        for s in sensors:
            sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, s.w1_id)
            temp = sensor.get_temperature()

            new_temp = Temperature.objects.create(sensor=s, value=temp, created=timestamp)
        time.sleep(temp_read_wait)


def check_relay():
    pass


def cleanup():
    while not stop_threads.isSet():
        oldest = timezone.now() - timezone.timedelta(days=30)
        oldest_timestamps = Timestamp.objects.filter(timestamp__lt=oldest)
        oldest_timestamps.delete()

        time.sleep(cleanup_wait)


if __name__ == '__main__':
    temp_thread = threading.Thread(target=read_temperature)
    temp_thread.daemon = True
    temp_thread.start()

    relay_thread = threading.Thread(target=check_relay)
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
