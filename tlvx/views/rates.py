# -*- coding: utf-8 -*-
from django.views.generic.list import ListView

from tlvx.core.models import Rates
from tlvx.serializers.rates import RatesSerializer


class RatesView(ListView):
    model = Rates
    template_name = 'client/rates/rates-simple.html'
    name = 'other'

    def get_queryset(self, **kwargs):
        return self.model.filter(name=self.name).order_by('-date_in')

    def get_context_data(self, **kwargs):
        data = RatesSerializer(instance=self.get_queryset(), many=True).data
        return data


class RatesPhysicalView(RatesView):
    template_name = 'client/rates/rates.html'
    name = 'p'

    def get_context_data(self, **kwargs):
        data = super(RatesPhysicalView, self).get_context_data(**kwargs)
        data['header'] = {
            'first': 'rates-internet',
            'second': 'rates-local',
            'third': 'rates-iptv',
        }
        return data
