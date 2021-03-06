#!/usr/bin/python
# -*- coding: utf-8 -*-

# Register your models here.

from Adeployment import models
from Adeployment.admin_base import site,BaseAdmin


class GroupInfoAdmin(BaseAdmin):
    list_display = ("name")
    list_filter = ["组名"]
    search_fields = ['name']


class VersionInfoAdmin(BaseAdmin):
    list_display = ("name")
    list_filter = ['版本号']
    search_fields = ['name']

class DeployListInfoAdmin(BaseAdmin):
    list_display = ('name')
    list_filter = ['名称']

class FilesInfoAdmin(BaseAdmin):
    list_display = ("name",'file_path','file_type','create_date')
    list_filter =  ["文件名","保存路径","文件类型","创建时间"]
    search_fields = ['name','file_type']

class HostInfoAdmin(BaseAdmin):
    list_display = ('hostname','address','port','username','password','group','version','script')
    list_filter = ["主机名",'IP地址','SSH端口号','用户名','密码','主机组','OpenShift版本','部署脚本']
    search_fields = ['hostname','address','version']

class FiletypeInfoAdmin(BaseAdmin):
    list_display = ("name")
    list_filter = ["模板类型"]
    search_fields = ('name')

class LogsFieldAdmin(BaseAdmin):
    list_display = ("name")
    list_filter = ["字段名"]

site.register(models.Host,HostInfoAdmin)
site.register(models.Group,GroupInfoAdmin)
site.register(models.Version,VersionInfoAdmin)
site.register(models.Files,FilesInfoAdmin)
site.register(models.FileType,FiletypeInfoAdmin)
site.register(models.DeployList,DeployListInfoAdmin)
site.register(models.LogsField,LogsFieldAdmin)



