from django.db import models


class Config(models.Model):
    name = models.CharField(max_length=100, blank=True)
    value = models.CharField(max_length=100, blank=True)
    enabled = models.BooleanField(default=True)

    class Meta:
        unique_together = ("name", "value")
        ordering = ['name', 'value']

    def __str__(self):
        return '{}:{}'.format(self.name, self.value)


class Sensor(models.Model):
    name = models.CharField(max_length=100)
    w1_id = models.CharField(max_length=100, default='')

    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

    def current_temperature(self):
        return self.temperature_set.order_by('-created__timestamp')[0]


class Timestamp(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return '{}'.format(self.timestamp)


class Temperature(models.Model):
    sensor = models.ForeignKey(Sensor)
    created = models.ForeignKey(Timestamp, null=True, blank=True)
    value = models.FloatField()

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return '{}: {}'.format(self.sensor.name, self.value) 

    def created_timestamp(self):
        return self.created.timestamp
