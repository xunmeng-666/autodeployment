#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.template import Library
from django.utils.safestring import mark_safe
from Adeployment.admin import site

#标签文件


register = Library()

@register.simple_tag
def get_model_verbose_name(admin_class):
    return admin_class.model._meta.verbose_name

@register.simple_tag
def get_enable_objects (row,app_name,model_name,admin_class):

    row_str = "<th id='conn-status' class='text-center' data-editable='false'>"
    row_str += "<a href='/cluster/{admin_class}/{obj_host}' class='btn btn-xs btn-info' data-toggle='modal' >" \
               "编辑</a>  ".format(admin_class=admin_class.model._meta.model_name, obj_host=row.id, )
    row_str += "<a onclick='template_del(this)' class='host_del btn btn-xs btn-danger asset_del' value='2'>删除</a></td>"\
        .format(app_name=app_name, model_name=model_name, obj_id=row.id)
    row_str += "</th>"
    return mark_safe(row_str)


@register.simple_tag
def get_m2m_objects(admin_class,field_name,selected_objs):
    """
    1.根据field_name从admin_class.model反射出字段对象
    2.拿到关联表的所有数据
    3.返回数据
    :param admin_class:
    :param field_name:
    :return:
    """

    field_obj = getattr(admin_class.model,'%s'%field_name)
    all_objects = field_obj.rel.to.objects.all()
    return set(all_objects) - set(selected_objs)

@register.simple_tag
def get_selected_m2m_objects(form_obj,field_name):
    """
    1.根据field_name反射出form_obj.instance里的字段对象
    2. 拿到字段对象关联的所有数据
    :param form_obj:
    :param field:
    :return:
    """

    if form_obj.instance.id:
        field_obj = getattr(form_obj.instance, field_name)
        return field_obj.all()
    else:
        return []

@register.simple_tag
def build_table_row(row, admin_class, app_name, host_group):

    row_ele = ""
    row_ele += "<th class='text-center'><input type='checkbox'  class='row-obj' name ='_selected_obj'  value='{obj_id}'></th>".format(obj_id=row.id)

    try:
        for index, column_name in enumerate(admin_class.list_display):

            field_obj = row._meta.get_field(column_name)

            if field_obj.choices:
                column_display_func = getattr(row, 'get_%s_display' % column_name)
                column_val = column_display_func()
            else:

                column_val = getattr(row, column_name)
            if index == 0:
                if column_name == 'host':
                    td_ele = "<th class='text-center'><a>{column_val}</a></th>".format(column_val=column_val.hostname)

                else:
                    td_ele = "<th class='text-center'><a href='/host_info_view/'>{column_val}</a></th>".format(column_val=column_val)


            elif index == 3:
                td_ele = "<th class='text-center' id='{column_name}'><a>{column_val}<a></th>".format(column_name=column_name ,column_val=column_val)

            else:
                if column_name == 'host_group':
                    td_ele = "<th class='text-center'><a>{column_val}<a></th>".format(column_val=column_val.group_name)

                else:
                    td_ele = "<th class='text-center' id='{column_name}'><a>{column_val}<a></th>".format(column_name=column_name,column_val=column_val)
            row_ele += td_ele

    except Exception:
        pass
    return mark_safe(row_ele)

@register.simple_tag
def get_abs_value(loop_num , curent_page_number):
    """返回当前页与循环loopnum的差的绝对值"""
    return abs(loop_num - curent_page_number)

@register.simple_tag
def build_time(row):
    td = "<td class='text-center'>%s</td>" %row.create_date.strftime("%Y-%m-%d %H:%M:%S")
    return mark_safe(td)