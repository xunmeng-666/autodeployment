# -*- coding:utf-8-*-

from django.conf.urls import url, include
from cluster_monitor import views

# from cluster_monitor import urls
urlpatterns = [
    url(r'^$', views.monitor),

]