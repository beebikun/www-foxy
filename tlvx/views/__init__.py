# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import RequestContext, loader
from tlvx import helpers
from tlvx.api import serializers
from tlvx.core import models


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
