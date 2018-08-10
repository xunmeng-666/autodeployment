#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.shortcuts import render,redirect,HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from Adeployment import forms
from Adeployment.admin_base import site
from Adeployment.core.model_ansible import build_file
from Adeployment.core.model_func import save_file,delete_file
from Adeployment.core.rabbitmqs import Rabbit_Consumer
from dwebsocket import require_websocket,accept_websocket

from Adeployment.conf.conf import LOGS
import json
import threading
import os
import dwebsocket


@csrf_exempt
@login_required
def index(request):
    page_name = "Dashboard"
    return render(request,'index.html',locals())

@csrf_exempt
def account_login(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get('next') or '/')
        return {"status":'error'}
    return render(request, 'login.html', locals())

def account_logout(request,**kwargs):
    request.session.clear()
    logout(request)

    return redirect('/')


def admin_func():
    for app_name in site.registered_admins:
        admin_class = site.registered_admins[app_name]
        return admin_class


def get_filter_objs(request,admin_class):
    """返回filter的结果queryset"""

    filter_condtions = {}
    for k,v in request.GET.items():
        if k in ['_page','_q','_o']:
            continue
        if v:#valid condtion
            filter_condtions[k] = v

    queryset = admin_class.model.objects.filter(**filter_condtions)
    return queryset,filter_condtions

def get_search_objs(request,querysets,admin_class):
    """
    1.拿到_q的值
    2.拼接Q查询条件
    3.调用filter(Q条件)查询
    4. 返回查询结果
    :param request:
    :param querysets:
    :param admin_class:
    :return:
    """
    q_val = request.GET.get('_q') #None
    if q_val:
        q_obj = Q()
        q_obj.connector = "OR"
        for search_field in admin_class.search_fields: #2
            q_obj.children.append( ("%s__contains" %search_field,q_val) )

        search_results = querysets.filter(q_obj)#3
    else:
        search_results = querysets

    return search_results,q_val

def get_orderby_objs(request,querysets):
    """
    排序
    1.获取_o的值
    2.调用order_by(_o的值)
    3.处理正负号，来确定下次的排序的顺序
    4.返回
    :param request:
    :param querysets:
    :return:
    """
    orderby_key = request.GET.get('_o') #-id
    last_orderby_key = orderby_key or ''
    if orderby_key:
        order_column = orderby_key.strip('-')
        order_results = querysets.order_by(orderby_key)
        if orderby_key.startswith('-'):
            new_order_key = orderby_key.strip('-')
        else:
            new_order_key = "-%s"% orderby_key

        return order_results,new_order_key,order_column,last_orderby_key
    else:
        return querysets,None,None,last_orderby_key

def update_host(admin_class):
    obj = admin_class.model.objects.all()
    try:
        for host in obj.values('id', 'hostname'):
            obj.filter(id=host.get('id')).update(pod_count=obj.filter(pod__host_id=host.get('id')).count())
    except Exception:
        pass

@login_required
def deploy(request,no_render=False):
    page_name = "DeployMent"
    admin_class = admin_func().get('files')
    deployfunc = admin_func().get('deploylist').model.objects.values('id','name')
    model_name = admin_class.model._meta.verbose_name
    update_host(admin_class)
    form = forms.create_dynamic_modelform(admin_class.model)
    if request.method == "POST":  # admin action
        action_func_name = request.POST.get('admin_action')
        action_func = getattr(admin_class, action_func_name)
        selected_obj_ids = request.POST.getlist("_selected_obj")
        selected_objs = admin_class.model.objects.filter(id__in=selected_obj_ids)
        action_res = action_func(request, selected_objs)
        if action_res:
            return action_res
        return redirect(request.path)
    else:
        form_obj = form()
        querysets, filter_conditions = get_filter_objs(request, admin_class)
        querysets, q_val = get_search_objs(request, querysets, admin_class)
        querysets, new_order_key, order_column, last_orderby_key = get_orderby_objs(request, querysets)
        paginator = Paginator(querysets, admin_class.list_per_page)  # Show 25 contacts per page
        page = request.GET.get('_page')
        try:
            querysets = paginator.page(page)
        except PageNotAnInteger:
            querysets = paginator.page(1)
        except EmptyPage:
            querysets = paginator.page(paginator.num_pages)


    if no_render:
        return locals()
    else:
        return render(request, 'cluster/deploy.html', locals())

@csrf_exempt
def deploy_del(request):
    ret = {'status': 'true', 'error': 'false'}
    try:
        if request.method == 'POST':
            admin_class = admin_func().get('files')
            for get_id in request.GET.get('idAll').split(','):
                obj = admin_class.model.objects.get(id=get_id)
                filefunc = admin_class.model.objects.values('file_name', 'file_path', 'create_date').get(id=get_id)
                file_name = "%s%s-%s" % (filefunc['file_path'], filefunc['file_name'], filefunc['create_date'])
                delete_file(file_name)
                obj.delete()
            return HttpResponse(json.dumps(ret))
    except ValueError:
        pass
    return HttpResponse(json.dumps(ret))

@csrf_exempt
def deploy_file(request):

    ret = {'status': 'true', 'error': 'false'}
    if request.method == 'POST':
        admin_class = admin_func().get('files')
        inven_id = request.GET.get('inventory_id').split('=')[0]
        playb_id = request.GET.get('playbook_id').split('=')[0]
        t = threading.Thread(build_file(inven_id,playb_id,admin_class))
        t.start()
        t.join(10)
        ret.update({'status': 'false','error': 'true'})
        return HttpResponse(json.dumps(ret))
    return HttpResponse(status=404)

@csrf_exempt
def deploy_delete(request):

    admin_class = admin_func().get('files')
    for get_id in request.GET.get('idAll').split(','):
        obj = admin_class.model.objects.get(id=get_id)
        filefunc = admin_class.model.objects.values('file_name', 'file_path', 'create_date').get(id=get_id)
        file_name = "%s%s-%s" % (filefunc['file_path'], filefunc['file_name'], filefunc['create_date'])
        delete_file(file_name)
        obj.delete()
    return redirect('/cluster/template/')


@login_required
def hosts(request):
    admin_class = admin_func().get("host")
    model_name = admin_class.model.objects.all()
    return render(request,'cluster/hosts.html',locals())


@login_required
@csrf_exempt
def upload(request):
    ret = {'status':'true'}
    if request.method == 'POST':
        filename = request.FILES.get('filename')
        filetype = request.GET.get('file_type')
        if save_file(filename=filename,filetype=filetype):
            return HttpResponse(json.dumps(ret))
        ret.update({'status':'false','error': 'true'})
        return HttpResponse(json.dumps(ret))

@login_required
@csrf_exempt
def template(request,no_render=False):
    admin_class = admin_func().get('filetype')
    model_name = admin_class.model._meta.verbose_name
    form = forms.create_dynamic_modelform(admin_class.model)
    if request.method == 'POST':
        form_obj = form(data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            # return {'status':'success'}
            return redirect('/cluster/template/' ,locals())
    else:
        form_obj = form()
        querysets, filter_conditions = get_filter_objs(request, admin_class)
        querysets, q_val = get_search_objs(request, querysets, admin_class)
        querysets, new_order_key, order_column, last_orderby_key = get_orderby_objs(request, querysets)
        paginator = Paginator(querysets, admin_class.list_per_page)  # Show 25 contacts per page
        page = request.GET.get('_page')
        try:
            querysets = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            querysets = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            querysets = paginator.page(paginator.num_pages)

    if no_render:  # 被其它函数调用，只返回数据
        return locals()
    else:
        return render(request, 'cluster/template.html', locals())

@csrf_exempt
def template_del(request):
    ret = {'status': 'true', 'error': 'false'}
    try:
        if request.method =='POST':
            admin_class = admin_func().get('filetype')
            for get_id in request.GET.get('idAll').split(','):
                obj = admin_class.model.objects.get(id=get_id)
                obj.delete()
            return HttpResponse(json.dumps(ret))
    except ValueError:
        pass
    return HttpResponse(json.dumps(ret))

@csrf_exempt
def template_delete(request):

    admin_class = admin_func().get('filetype')
    for get_id in request.GET.get('idAll').split(','):
        obj = admin_class.model.objects.get(id=get_id)
        obj.delete()

    return redirect('/cluster/template/')

@require_websocket
def echo_logs(request):
    msg = request.websocket.wait()
    run_mq = Rabbit_Consumer()
    if msg == 'quit':
        run_mq.rabbit_close()
    else:
        run_mq.rabbit_consumer(request)

@require_websocket
def echo_logfile(request):
    logs_name = request.GET.get('LogName')
    msg = request.websocket.wait()
    file = open(logs_name,'r')
    for content in file.readlines():
        request.websocket.send("%s"%content.encode('utf-8'))
    file.close()
    request.websocket.close()


@require_websocket
def echo_logfiles(request):
    msg = request.websocket.wait()
    admin_class = admin_func().get('deploylist')
    log_name = admin_class.model.objects.all().values('name').order_by('-id')[0]['name']
    file = open(log_name,'r')
    for content in file.readlines():
        request.websocket.send("%s"%content.encode('utf-8'))
    file.close()

