# -*- coding: utf-8 -*-
import math
import re
from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import RequestContext, loader
from tlvx import settings
from tlvx.api import serializers
from tlvx.core import models
from tlvx.helpers import change_keyboard


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


def paginator(count, cur):
    """Утилита для паджинатора(страница новости).
    Паджинатор представляет собой уи, в котором можно перейти на
    страницу вперед, на страницу назад, в нем отображается текущая страница,
    а также некоторое количество(settings.PAGINATOR_PAGE) страниц, соседних
    с текущей. Остальные страницы заменены на (..).
    Т.е, паджинатор имеет вид
    <-(1)(...)(10)(11)(12)(...)(LAST)->
    Так вот, данная функция считает и возвращает список номеров страниц,
    которые будут отображаться вместо (10)(11)(12).
    Args:
        - count - int, количество страниц всего
        - cur - int, номер текущей страницы
    Returns:
        Список из int
    """
    #Проверяем, что settings.PAGINATOR_PAGE - нечетное. иначе - отнимаем 1
    paginator_page = settings.PAGINATOR_PAGE if (
        settings.PAGINATOR_PAGE % 2) else settings.PAGINATOR_PAGE - 1
    #Определяем действительное количество отображаемых страниц
    #Для этого отнимает 4 страницы(вперед, назад, (...), (...))
    displayP = paginator_page - 4
    empty = ['...']
    #Определяем, какое количество страниц будет отображаться справа
    #и слева от текущей
    half = (displayP-1)/2
    left = cur - half  # левый край
    right = cur + half + 1  # правый край

    if left <= 2:  # для случаев <-(1)(2)(3)(...)(LAST)->
        pages = range(2, displayP + 1) + empty
    elif right >= count:  # для случаев <-(1)(...)(51)(52)(53)->
        pages = empty + range(count - displayP + 1, count)
    else:  # для случаев <-(1)(...)(10)(11)(12)(...)(53)->
        pages = empty + range(left, right) + empty
    return [1] + pages + [count]


def my_response(request, context={}, name=''):
    """
    Args:
        -request
        -context - контекст темлейта
        -name - имя темплейта
    Returns:
        -HttpResponse с нужным темплейтом
    """
    name = name or request.META.get('PATH_INFO').split('/')[-1]
    context = RequestContext(request, {'data': context})
    template = loader.get_template('client/%s.html' % name)
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
    """
    params = dict(
        street=change_keyboard(request.POST.get('street')),
        num=request.POST.get('num'))

    def get_data(obj, result=False):
        if not obj:
            return
        data = serializers.BuildingSerializer(instance=obj).data
        data[u'co'] = obj.co and (obj.co.contacts + ', ' + obj.co.schedule)
        data['result'] = result
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
        data['result'].extend(map(get_data,
                                  models.Building.filter_simmular(**params)))
        return data['result'] and data

    return my_response(request, get(params) or dict(params=params), 'letsfox')


###############################
#Новости

def news(request, pk=None, template='news', additional_data=None):
    """Возвращаеи страницу со списком новостей. Также используется в index"""
    get_data = lambda obj: serializers.NoteSerializer(instance=obj).data
    data = dict()
    if not pk:
        #Возвращаем требуемое settings.NOTE_COUNT
        #новостей на требуемой странице
        try:
            #Вместо page может быть прислана фигня, поэтому лучше проверить
            page = int(request.GET.get('page', 1))
        except ValueError:
            page = 1
        params = dict(count=settings.NOTE_COUNT, page=page)
        first = params['count']*(params['page']-1)
        end = params['count']*params['page']
        objects = models.Note.objects.all().order_by('num', '-date')[first:end]
        data.update(
            page=params['page'],
            page_count=int(math.ceil(
                models.Note.objects.all().count()/float(params['count'])))
        )
        #Следующие 3 поля - для пэйджинатора, чтобы не делать этого в клиенте
        data['display_page'] = paginator(data['page_count'], data['page'])
        data['prev_page'] = data['page']-1 if data['page'] != 1 else 1
        data['next_page'] = data['page']+1 if (
            data['page'] != data['page_count']) else data['page_count']
    else:
        #Возвращаем требуемую нововсть
        objects = [get_object_or_404(models.Note, pk=pk)]
    data['result'] = map(get_data, objects)
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
        rtype__name=self.name).order_by('-date_in')

    def __init__(self, request, name, template='rates-simple'):
        data = map(self.get_data, self.get_object(name))
        self.response = my_response(request, context=data, name=template)


def rates(request):
    """Тарифы для физ лиц"""
    return Rates(request, name='p', template='rates').response


def rates_simple(request, name):
    """Тарифы для юр лиц и прочее"""
    return Rates(request, name).response


###############################
#Оплата услуг

def payment(request, name=None):
    """Выбор типа оплаты"""
    return my_response(request, name='payment')


def paymentcard(request):
    """Карты"""
    objects = models.Payment.objects.filter(is_terminal=False).order_by('num')
    data = [serializers.PaymentSerializer(instance=obj).data
            for obj in objects]
    return my_response(request, data, name='payment-card')


def paymentelmoney(request):
    """Эл деньги (Асист)"""
    page = lambda n: serializers.StaticPageSerializer(
        instance=models.StaticPage.objects.get(name=n)).data
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
    def get_point_data(obj):
        data = serializers.PaymentPointSerializer(instance=obj).data
        name = data['name'].replace('&', '&amp;')
        while name.find('"') >= 0:
            i = name.find('"')
            name = name[:i] + '&laquo;' + name[i+1:]
            i = name.find('"')
            name = name[:i] + '&raquo;' + name[i+1:]
        data['name'] = name or data['address']
        del data['schedule']
        del data['contacts']
        return data

    def get_data(obj):
        data = serializers.PaymentSerializer(instance=obj).data
        data['points'] = {}
        if data['name'] != u'Офисы продаж':
            name = data['name'].replace(u'&', u'&amp;')
            while name.find('"') >= 0:
                i = name.find('"')
                name = name[:i] + '&laquo;' + name[i+1:]
                i = name.find('"')
                name = name[:i] + '&#187;' + name[i+1:]
            data['name'] = name
            point_total = obj.get_values()
            point_result = map(get_point_data, obj.get_points())
        else:
            co_list = models.CentralOffice.objects.filter(in_map=True)
            point_total = len(co_list)
            point_result = map(get_point_data, co_list)
            #Заменяем ид в офисах продаж, потому что
            #ид с 1 по 3 уже заняты другими ppoint
            ppoint_count = models.PaymentPoint.objects.aggregate(
                Max('id')).get('id__max')
            for i in range(len(point_result)):
                co = point_result[i]
                co['id'] = co['id'] + ppoint_count
                point_result[i] = co
        data['points']['total'] = point_total
        data['points']['result'] = point_result
        return data
    objects = models.Payment.objects.filter(is_terminal=True)
    data = [get_data(obj) for obj in objects]
    return my_response(request, data, 'payment-terminal')


###############################
#О компании

def about(request):
    """Контакты"""
    def get_data(obj):
        data = serializers.PaymentPointSerializer(instance=obj).data
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
