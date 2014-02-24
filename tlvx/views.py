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
    maxP = not settings.PAGINATOR_PAGE and settings.PAGINATOR_PAGE or \
        settings.PAGINATOR_PAGE-1
    displayP = maxP - 4
    half = (displayP-1)/2
    display_page = []
    for i in range(1, count+1):
        if i == 1 or i == count or i == cur:
            if i == cur:
                display_page.append(i)
            else:
                display_page.append(i)
        elif (displayP+half) > count:
            if i >= (count-displayP):
                display_page.append(i)
            if i == (count-displayP-1):
                display_page.append('...')
        elif cur <= half:
            if i <= displayP:
                display_page.append(i)
            if i == (displayP+1):
                display_page.append('...')
        else:
            if (cur-half-1) == i:
                display_page.append('...')
            elif (cur-half) <= i and i < cur:
                display_page.append(i)
            elif (cur+half) >= i and i > cur:
                display_page.append(i)
            elif (cur+half+1) == i:
                display_page.append('...')
            else:
                pass
    return display_page


def my_response(request, context={}, name=''):
    name = name or request.META.get('PATH_INFO').split('/')[-1]
    context = RequestContext(request, {'data': context})
    template = loader.get_template('client/%s.html' % name)
    return HttpResponse(template.render(context))


class StaticPage:
    def __init__(self, request, name='', model='StaticPage', template=''):
        self.name = name or request.META.get('PATH_INFO').split('/')[-1]
        self.model = model
        obj = self.get_obj()
        self.data = self.get_data(obj)
        if obj.get_child():
            self.data['childs'] = self.get_child_data(obj)
        template = template or name
        self.response = my_response(request, self.data, template)

    def get_data(self, obj):
        return serializers.StaticPageSerializer(instance=obj).data

    def sub_get_child_data(self, lst, obj):
        i = lst.index(obj)
        data = self.get_data(obj)
        return i, data

    def get_child_data(self, obj):
        child_list = obj.get_child()
        for child_obj in child_list:
            i, child_data = self.sub_get_child_data(child_list, child_obj)
            sub_list = child_obj.get_child()
            if sub_list:
                for sub_obj in sub_list:
                    sub_i, sub_data = self.sub_get_child_data(
                        sub_list, sub_obj)
                    sub_sub_list = sub_obj.get_child()
                    if sub_sub_list:
                        for sub_sub_obj in sub_sub_list:
                            sub_sub_i, sub_sub_data = \
                                self.sub_get_child_data(
                                    sub_sub_list, sub_sub_obj)
                            sub_sub_list[sub_sub_i] = sub_sub_data
                        sub_data['childs'] = sub_sub_list
                    sub_list[sub_i] = sub_data
                child_data['childs'] = sub_list
            child_list[i] = child_data
        return child_list

    def get_obj(self):
        return get_object_or_404(getattr(models, self.model), name=self.name)


def map_page(request):
    return my_response(request, name="map")

###############################################################################


def about(request):
    def get_data(obj):
        data = serializers.PaymentPointSerializer(instance=obj).data
        data['ico'] = obj.marker and obj.marker.name
        return data

    def get_objects():
        return models.CentralOffice.objects.filter(in_map=True)

    objects = get_objects()
    data = dict(result=[get_data(obj) for obj in objects])
    return my_response(request, data)


def accessdenied(request):
    return my_response(request, name="access-denied")


def documents(request):
    return StaticPage(request=request, model='DocumentsPage').response


def index(request):
    return news(request, template='index')


def how(request):
    return StaticPage(request=request, model='HelpPage').response


def letsfox(request):
    def filter_objects_simular(**params):
        return filter(
            lambda b: b.search_by_address(
                street=params.get('street'), num=params.get('num')),
            models.Building.objects.exclude(
                id=params.get('result') and params.get('result').id or 0)
            )

    def get_data(obj):
        data = {}
        if obj:
            data = serializers.BuildingSerializer(instance=obj).data
            data[u'co'] = obj.co and (obj.co.contacts + ', ' + obj.co.schedule)
        return data

    def get_street(name):
        serializer = serializers.StreetSerializer(data={'name': name})
        if serializer.is_valid():
            street = serializer.object
        else:
            street_set = filter(
                lambda s: s.name.lower() == name.lower(),
                models.Street.objects.all())
            street = street_set and street_set[0]
        return street

    def get(params):
        if not params.get('street') or not params.get('num'):
            return
        data = dict(result=[], params=params)
        street = get_street(params['street'])
        if street:
            serializer = serializers.BuildingSerializer(
                data={'num': params['num'], 'street': street.pk})
            if not serializer.is_valid():
                return
            params['result'] = serializer.object
            data['result'].append(
                dict(result=True, **get_data(params['result'])))
        data['result'] = data['result'] + \
            map(get_data, filter_objects_simular(**params))
        return data['result'] and data
    params = dict(
        street=change_keyboard(request.POST.get('street')),
        num=request.POST.get('num'))
    data = get(params) or {'params': params}
    return my_response(request, data, 'letsfox')


def news(request, pk=None, template='news'):
    def get_data(obj):
        return serializers.NoteSerializer(instance=obj).data
    data = dict()
    if not pk:
        params = dict(
            count=request.GET.get('count') or settings.NOTE_COUNT,
            page=request.GET.get('page') or 1
        )
        try:
            params = dict([(k, int(v)) for (k, v) in params.items()])
        except ValueError, e:
            params = dict(count=settings.NOTE_COUNT, page=1)
        first = params['count']*(params['page']-1)
        end = params['count']*params['page']
        objects = models.Note.objects.all().order_by('num', '-date')[first:end]
        data.update(
            page=params['page'],
            page_count=int(math.ceil(
                models.Note.objects.all().count()/float(params['count'])))
        )
        data['display_page'] = paginator(data['page_count'], data['page'])
        data['prev_page'] = data['page']-1 if data['page'] != 1 else 1
        data['next_page'] = data['page']+1 if (
            data['page'] != data['page_count']) else data['page_count']
    else:
        objects = [get_object_or_404(models.Note, pk=pk)]
    data['result'] = map(get_data, objects)
    return my_response(request, data, template)


def payment(request, name=None):
    if name:
        template_name = 'way' if name not in ['limit'] else name
        return StaticPage(
            request=request, name='payment-%s' % name,
            template='payment-%s' % template_name).response
    else:
        return my_response(request, name='payment')


def paymentcard(request):    
    objects = models.Payment.objects.filter(is_terminal=False).order_by('num')
    data = [serializers.PaymentSerializer(instance=obj).data
            for obj in objects]
    return my_response(request, data, name='payment-card')


def paymentmobile(request):
    context = dict()
    gray_ip = is_gray_ip(request.META['REMOTE_ADDR'])
    return my_response(request, name="payment-mobile", context=dict(gray_ip=gray_ip))


def paymentterminal(request):
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


class Rates:
    def __init__(self, request, name, template='rates-simple'):
        self.name = name
        data = [self.get_data(obj) for obj in self.get_object()]
        self.response = my_response(request, context=data, name=template)

    def get_object(self):
        return models.Rates.objects.filter(
            rtype__name=self.name).order_by('-date_in')

    def get_data(self, obj):
        return serializers.RatesSerializer(instance=obj).data


def rates(request):
    return Rates(request, name='p', template='rates').response

def rates_simple(request, name):
    return Rates(request, name).response


def simple_content(request, page=None):
    return StaticPage(request=request, template='simple-content').response

def vacancy(request):
    return StaticPage(request=request, model='VacancyPage').response


########################################


def main(request, name):
    template = loader.get_template('client/%s.html' % name)
    context = RequestContext(request, {})
    return template.render(context)
