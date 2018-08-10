# -*- coding:utf-8-*-
import os
import datetime

#定义配置文件路径
BASH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#LOG配置
LOG_NAME = "ADAdmin"
#LOGS = "%s/logs/%s" %(BASH,LOG_NAME)
LOGS = "/var/log/adadmin/%s" %(LOG_NAME)
FILE_PATH = "/etc/ansible/roles/"
#FILE_PATH = "%s/statics/files/" %BASH

#RabbitMQ配置
#RABBITMQ_HOST = "localhost"
RABBITMQ_HOST = "10.211.55.2"
RABBITMQ_PORT = 5672