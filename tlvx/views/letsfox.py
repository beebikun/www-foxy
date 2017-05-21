# -*- coding: utf-8 -*-
from django.views.generic import TemplateView

from tlvx.core.models import Building, Street, ConnRequest
from django.http import HttpResponseRedirect
from django.db.models import Q
from rest_framework import serializers
import json
from rest_framework.reverse import reverse


def find__simmular_building(street, num):
    return Building.objects.filter(Q(street__name__icontains=street, num__icontains=num) |
                                   Q(street_alt__name__icontains=street, num_alt__icontains=num))


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
            # i'm a lame - ленина and Ленина have different first symbols in unicode,
            # idk what to do with that, but _icontains doesn't work
            simmular = Building.objects.filter(
                # starts with that
                Q(street__name__contains=street_name.capitalize(), num__icontains=num) |
                Q(street_alt__name__contains=street_name.capitalize(), num_alt__icontains=num) |
                # in the middle
                Q(street__name__contains=street_name, num__icontains=num) |
                Q(street_alt__name__contains=street_name, num_alt__icontains=num)
            )
            street = Street.objects.filter(name__iexact=street_name.capitalize()).first()
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
