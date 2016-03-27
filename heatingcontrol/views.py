import csv
import time
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Config, Sensor, Temperature, Timestamp

def index(request):
    [oven, created] = Config.objects.get_or_create(name__exact='ofen')
    sensors = Sensor.objects.all()
    end_window = time.mktime(time.localtime())*1000
    start_window = end_window - 1000*3600*3
    return render_to_response(
        'index.html',
        locals()
    )


def csv_temperatures(request, sensor_id):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="temperatures.csv"'
    
    writer = csv.writer(response)
    
    if sensor_id == 'all':
        sensors = Sensor.objects.all()
    else:
        sensors = Sensor.objects.filter(id=sensor_id)
    
    header = ['Date']
    header.extend(['{}'.format(sensor.name) for sensor in sensors])
    writer.writerow(header)
    
    timestamps = Timestamp.objects.all().order_by('timestamp')
    for t in timestamps:
        line = [timezone.localtime(t.timestamp).strftime('%Y/%m/%d %H:%M')]
        line.extend([temp.value for temp in t.temperature_set.filter(sensor__in=sensors).order_by('sensor__name') if temp is not None])
        if len(line) > 1:
            writer.writerow(line)

    return response


@login_required
def toggle_oven(request):
    oven = Config.objects.get(name__exact='ofen')

    oven.enabled = not oven.enabled
    oven.save()

    return redirect('index')


@login_required
def toggle_alarm(request, alarm_name):
    try:
        c = Config.objects.get(config_type='ALARM', name=alarm_name)
        c.enabled = not c.enabled
        c.save()
        return HttpResponse('{} set to {}'.format(alarm_name, c.enabled))
    except Config.DoesNotExist:
        return HttpResponse('failed to set {}'.format(alarm_name))
