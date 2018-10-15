# -*- coding: utf-8 -*-
from django.views.generic import TemplateView

from tlvx.core.models import Building, Street, ConnRequest
from django.http import HttpResponseRedirect
from django.db.models import Q
from rest_framework import serializers
import json
from rest_framework.reverse import reverse

from operator import __or__ as OR


def get_street_name_variances(street_name, fn):
    variances = [
        street_name.strip(),
        street_name.strip().replace(u'е', u'ё'),
        street_name.strip().replace(u'ё', u'е')
    ]
    results = []
    for street_name in variances:
        results.extend(fn(street_name))
    return results


def get_strict_street_name_variances(street_name):
    def get(street_name):
        def split_by(split):
            capitalize = lambda s: s.capitalize()
            splitted = street_name.split(split)
            capitalized = map(capitalize, splitted)
            return ['-'.join(capitalized), ' '.join(capitalized)]
        return [street_name] + split_by(' ') + split_by('-')

    return get_street_name_variances(street_name, get)


def get_notstrict_street_name_variances(street_name):
    def get(street_name):
        # in the middle
        return [
            street_name.lower(),
            street_name.lower().split('-')[0],
            street_name.lower().split(' ')[0],
        ]
    return get_strict_street_name_variances(street_name) + \
        get_street_name_variances(street_name, get)


def find_simmular_building(street_name, num):
    # i'm a lame - ленина and Ленина have different first symbols in unicode,
    # idk what to do with that, but _icontains doesn't work
    street_name_variances = get_notstrict_street_name_variances(street_name)
    queries = []
    for street_name in street_name_variances:
        queries.append(Q(street__name__contains=street_name, num__icontains=num))
        queries.append(Q(street_alt__name__contains=street_name, num_alt__icontains=num))

    return Building.objects.filter(reduce(OR, queries))


def find_street(street_name):
    street_name_variances = get_strict_street_name_variances(street_name)
    queries = []
    for street_name in street_name_variances:
        queries.append(Q(name__iexact=street_name))
    return Street.objects.filter(reduce(OR, queries)).first()


class ConnRequestSerializer(serializers.ModelSerializer):
    fio = serializers.CharField(required=True, max_length=128,
                                error_messages=dict(required=u"Пожалуйста, укажите своё имя"))
    address = serializers.CharField(required=True)
    status = serializers.CharField(required=True)

    phone = serializers.CharField(required=True, max_length=128,)  # TODO: replace with `contact`

    flat = serializers.CharField(required=False, max_length=128)
    source = serializers.CharField(required=False, max_length=512)
    comment = serializers.CharField(required=False, max_length=512)

    class Meta:
        model = ConnRequest
        fields = ('fio', 'address', 'status', 'phone', 'flat', 'source', 'comment', )


class LetsFoxView(TemplateView):
    template_name = "client/letsfox/letsfox.html"

    def post(self, request):
        # post a new conn request
        data = request.POST
        s = ConnRequestSerializer(data=data)
        if s.is_valid():
            ConnRequest.objects.create(**s.data)
            ConnRequest.objects.sendAll()
            return self.render_to_response({'created': True})
        building = Building.objects.get(id=data.get('building-id'))
        errors = ','.join(s.errors.keys())
        url = u'{}?street={}&num={}&errors={}&id={}'.format(
            reverse('client-letsfox'), building.street.name, building.num, errors, building.id)
        return HttpResponseRedirect(url)

    def get(self, request, errors=False):
        street_name = request.GET.get('street')
        num = request.GET.get('num')
        errors = request.GET.get('errors')
        if errors:
            errors = errors.split(',')
            errors = dict(zip(errors, [True] * len(errors)))
            context = {'result': Building.objects.filter(id=request.GET.get('id')).first(),
                       'errors': errors}
            return self.render_to_response(context)

        simmular = Building.objects.none()
        result = None
        if street_name and num:
            simmular = find_simmular_building(street_name, num)
            street = find_street(street_name)
            if street is not None:
                result = Building.objects.filter(
                    Q(street_id=street.id, num=num) |
                    Q(street_alt_id=street.id, num_alt=num)).first()
                if result is None:
                    try:
                        # it will try to get position from 2gis during saving
                        # if 2gis don't know this place - 2gis will raise an exaption
                        result = Building.objects.create(street=street, num=num)
                    except:
                        pass
        if result:
            simmular = simmular.exclude(id__in=[result.id])
        context = {'result': result, 'simmular': simmular[:10], 'errors': errors}
        return self.render_to_response(context)
