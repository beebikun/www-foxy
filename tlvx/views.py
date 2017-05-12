# -*- coding: utf-8 -*-
import re
from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
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


class StaticPage:
    """
    """
    def __init__(self, request, name='', model='StaticPage', template=''):
        """
        Args:
            -request
            -name - имя страницы в бд
            -template - имя нужного темлейта,
                если он не совпадает с именем страницы в бд
        Returns:
            -my_response
        """
        self.name = name or request.META.get('PATH_INFO').split('/')[-1]
        self.model = model
        obj = self.get_obj()  # непосредственно сам объект
        if obj.get_child():  # для страниц вида Tree (вакансии, справка)
            self.data = self.get_child_data(obj)
        else:
            self.data = self.get_data(obj)  # сериализованные данные
        self.response = my_response(request, self.data, template or name)

    def get_data(self, obj):
        return serializers.StaticPageSerializer(instance=obj).data

    def get_child_data(self, obj):
        """Рекурсивно обходит все obj, имеющие child и возвращает дата"""
        data = self.get_data(obj)
        if obj.get_child():
            data['childs'] = map(self.get_child_data, obj.get_child())
        return data

    def get_obj(self):
        return get_object_or_404(getattr(models, self.model), name=self.name)

#Простой сериалайзер статических страниц по имени
page = lambda n: serializers.StaticPageSerializer(
    instance=models.StaticPage.objects.get(name=n)).data


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
########Static pages
###############################

def simple_content(request, page=None):
    """Для отображения простых static page"""
    return StaticPage(request=request, template='simple-content').response


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
#Интернет -см static page


###############################
#Тарифы


class Rates:
    """Класс для rates и rates_simple"""

    get_data = lambda self, obj: serializers.RatesSerializer(instance=obj).data

    #Возвращает тарифы нужного типа(pp, jp, other),
    #отсортированный по убыванию даты
    get_obj = lambda self, name: models.Rates.objects.filter(
        rtype__name=name).order_by('-date_in')

    def __init__(self, request, name,
                 template='rates-simple', additional_data=None):
        data = dict(result=map(self.get_data, self.get_obj(name)))
        if additional_data:
            data.update(additional_data)
        self.response = my_response(request, context=data, name=template)


def rates(request):
    """Тарифы для физ лиц"""
    additional_data = {'tv_count': models.StaticPage.objects.get(name='tv_count').content}
    return Rates(request, name='p',
                 template='rates', additional_data=additional_data).response


def rates_jp(request):
    """Rates for jp"""
    additional_data = dict(
        docs=models.StaticPage.objects.get(name="jp-docs").content)
    return Rates(request, name='jp',
                 template='rates-jp',
                 additional_data=additional_data).response


def rates_simple(request, name):
    """прочее"""
    return Rates(request, name).response


###############################
#Оплата услуг

def payment(request, name=None):
    """Выбор типа оплаты"""
    return my_response(request, name='payment')


def paymentcard(request):
    """Карты"""
    objects = models.Payment.objects.filter(is_terminal=False).order_by('num')
    data = {obj.id:serializers.PaymentSerializer(instance=obj).data
            for obj in objects}
    return my_response(request, data, name='payment-card')


def paymentelmoney(request):
    """Эл деньги (Асист)"""
    data = dict(instruction=page('asist-instruction'),
                returns=page('asist-returns'), inn=page('payment-elmoney-inn'))
    return my_response(request, data, name='payment-elmoney')


def paymentlimit(request):
    """Взятие лимита"""
    return StaticPage(request=request, name='payment-limit').response


def paymentmobile(request):
    """Мобильные платежи"""
    gray_ip = is_gray_ip(request.META['REMOTE_ADDR'])
    return my_response(request, name="payment-mobile",
                       context=dict(gray_ip=gray_ip))


def paymentterminal(request):
    """Наличные и терминалы"""
    def _clear(s):
        if not s:
            return
        s = s.replace('&', '&amp;')
        while s.find('"') >= 0:
            i = s.find('"')
            s = s[:i] + '&laquo;' + s[i+1:]
            i = s.find('"')
            s = s[:i] + '&raquo;' + s[i+1:]
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


###############################
#О компании

def about(request):
    """Контакты"""
    def get_data(obj):
        data = serializers.COSerializer(instance=obj).data
        data['ico'] = obj.marker and obj.marker.name
        return data

    data = dict(result=map(get_data,
                           models.CentralOffice.objects.filter(in_map=True)))
    return my_response(request, data)


def documents(request):
    """Документы (Tree Page)"""
    return StaticPage(request=request, model='DocumentsPage').response


def vacancy(request):
    """Вакансии (Tree Page)"""
    return StaticPage(request=request, model='VacancyPage').response


###############################
#Справка

def how(request):
    """Справка"""
    return StaticPage(request=request, model='HelpPage').response


# def accessdenied(request):
#     """
#     """
#     return my_response(request, name="access-denied")

########################################


# def main(request, name):
#     """
#     """
#     template = loader.get_template('client/%s.html' % name)
#     context = RequestContext(request, {})
#     return template.render(context)
