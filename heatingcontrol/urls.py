"""doorguard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from . import views

urlpatterns = [
    url('admin/', admin.site.urls),
    url(r'^$', views.index, name='index'),
    url(r'^csv_temp/(?P<sensor_id>[a-z0-9]+)/$', views.csv_temperatures, name='csv-temperatures'),
    url(r'^toggle_oven/$', views.toggle_oven, name='toggle-oven'),
]
