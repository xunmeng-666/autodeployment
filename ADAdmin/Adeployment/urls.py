# -*- coding:utf-8-*-

from django.conf.urls import url,include
from Adeployment import views
# from cluster_monitor import urls
urlpatterns = [
    url(r'^$', views.index),
    # url(r'^login/$', views.login),
    url(r'deploy/$', views.deploy),
    url(r'deploy/all_del/$', views.deploy_del),
    url(r'deploy/del/$', views.deploy_delete),
    url(r'deploy/file/$', views.deploy_file),
    url(r'template/$', views.template),
    url(r'template/all_del/$', views.template_del),
    url(r'template/del/$', views.template_delete),
    url(r'hosts/$', views.hosts),
    url(r'upload/$', views.upload),
    url(r'echo_logs/$', views.echo_logs),
    url(r'echo_logfile/$', views.echo_logfile),
    url(r'echo_logfiles/$', views.echo_logfiles),
    # url(r'cluster_monitor/$', include("cluster_monitor.urls")),

]