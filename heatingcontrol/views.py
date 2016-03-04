from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .models import Device, Log, Config

def index(request):

    return render_to_response(
        'index.html',
        locals()
    )


@login_required
def toggle_alarm(request, alarm_name):
    try:
        c = Config.objects.get(config_type='ALARM', name=alarm_name)
        c.enabled = not c.enabled
        c.save()
        return HttpResponse('{} set to {}'.format(alarm_name, c.enabled))
    except Config.DoesNotExist:
        return HttpResponse('failed to set {}'.format(alarm_name))
