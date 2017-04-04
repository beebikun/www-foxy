# -*- coding: utf-8 -*-
import re
from django.db.models import Max
from django.http import HttpResponse
from django.template import RequestContext, loader
from tlvx import helpers
from tlvx.api import serializers
from tlvx.core import models


def is_gray_ip(ip):
    """Определяет, является ли полученный ip серым

    Args:
        ip - str
    Returns:
        True/False
    """
    ip = re.match('[\d]+.[\d]+.[\d]+.[\d]+', ip)
    if not ip:
        return
    A, B, C, D = [int(i) for i in ip.group().split('.')]
    if A == 10:
        return True
    if A == 172 and 16 <= B <= 31:
        return True
    if A == 192 and B == 168:
        return True
    return False


def my_response(request, context={}, name=''):
    """
    Args:
        -request
        -context - контекст темлейта
        -name - имя темплейта
    Returns:
        -HttpResponse с нужным темплейтом
    """
    path_info = filter(lambda i: i and i != '!',
                       request.META.get('PATH_INFO').split('/'))
    name = 'client/%s.html' % (name if name else path_info[0])
    context = RequestContext(request, {'data': context})
    template = loader.get_template(name)
    return HttpResponse(template.render(context))


###############################################################################

###############################
########Служебнные страницы
###############################

def map_page(request):
    """Служебная страница, где можно по клику получить координаты(lonlat)"""
    return my_response(request, name="map")


def index(request):
    """Главная страница"""
    images = models.Image.objects.filter(is_displ=True).order_by('num')
    banner = [dict(serializers.ImageSerializer(instance=img).data,
                   **{'url': img.get_img_absolute_urls(), 'num': i}) for i, img
              in enumerate(images)]
    return news(request, template='index', additional_data=dict(banner=banner))


###############################
########Menu sections
###############################


###############################
#Подключиться

def letsfox(request):
    """В request.POST должны быть
        'street' - название улицы, регистр и раскладка не важены,
        'num' - номер дома

    Это немного странно сделано, но в данном случае пост возвращает адреса,
    с указанием их статуса (подключен, сбор заявок, не подключен),
    чтобы можно было выбрать один из них в клиенте и оставить заявку.
    А вот сама заявка делается через апи.
    """
    strt = request.POST.get('street', '')
    params = dict(
        street=helpers.change_keyboard(strt) if strt else strt,
        num=request.POST.get('num', ''))

    def get_data(obj, result=False):
        if not obj:
            return
        data = serializers.BuildingSerializer(instance=obj).data
        data[u'co'] = obj.co and '%s, %s' % (
            obj.co.contacts or '', obj.co.schedule or '')
        data['result'] = result
        data['status'] = u'Подключен' if obj.active else (
            u'Сбор заявок' if obj.plan else u'Не подключен')
        return data

    def get(params):
        if not params.get('street') or not params.get('num'):
            return
        data = dict(result=[], params=params)
        street_serializer = serializers.StreetSerializer(
            data={'name': params['street']})
        if street_serializer.is_valid():
            street = street_serializer.object
            serializer = serializers.BuildingSerializer(
                data={'num': params['num'], 'street': street.pk})
            if serializer.is_valid():
                params['result'] = serializer.object
                data['result'] = [get_data(params['result'], True)]
        data['result'].extend(
            map(get_data, models.Building.objects.filter_simmular(**params)))
        return data['result'] and data

    return my_response(request, get(params) or dict(params=params), 'letsfox')


###############################
#Новости

def news(request, pk=None, template='news', additional_data=None):
    """Возвращаеи страницу со списком новостей. Также используется в index"""
    data = helpers.get_news(
        srlz=serializers.NoteSerializer, model=models.Note,
        page=request.GET.get('page', 1), pk=pk)
    if additional_data:
        #Т.к эту же функцию использует еще и index, то есть возможность
        #запихать в контекст что-нибудь еще
        data.update(additional_data)
    return my_response(request, data, template)


###############################
#Оплата услуг


def paymentterminal(request):
    """Наличные и терминалы"""
    def _clear(s):
        if not s:
            return
        s = s.replace('&', '&amp;')
        while s.find('"') >= 0:
            i = s.find('"')
            s = s[:i] + '&laquo;' + s[i + 1:]
            i = s.find('"')
            s = s[:i] + '&raquo;' + s[i + 1:]
        return s

    def get_point_data(obj):
        data = serializers.PaymentPointSerializer(instance=obj).data
        data['name'] = _clear(data.get('name', data.get('address')))
        if isinstance(obj, models.CentralOffice):
            #Заменяем ид в офисах продаж, потому что
            #их ид уже заняты другими ppoint
            data['id'] = models.PaymentPoint.objects.aggregate(
                Max('id')).get('id__max') + data['id']
        return data

    def get_data(obj):
        data = serializers.PaymentSerializer(instance=obj).data
        data['name'] = _clear(data['name'])
        if data['name'] != u'Офисы продаж':
            points = obj.get_points()
        else:
            points = models.CentralOffice.objects.filter(in_map=True)
        data['points'] = dict(total=(points),
                              result=map(get_point_data, points))
        return data

    objects = models.Payment.objects.filter(is_terminal=True)
    data = [get_data(obj) for obj in objects]
    return my_response(request, data, 'payment-terminal')
