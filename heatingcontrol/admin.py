from django.contrib import admin

from .models import Config, Sensor, Temperature 

admin.site.register(Sensor)

@admin.register(Temperature)
class TemperatureAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created_timestamp')
    list_filter = ('sensor',)

@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'enabled')
    list_per_page = 30

