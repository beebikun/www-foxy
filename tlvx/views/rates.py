# -*- coding: utf-8 -*-
from django.views.generic.detail import DetailView
from rest_framework import serializers

from tlvx.core.models import Rates


class RatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rates


class RatesView(DetailView):
    model = Rates
    template_name = 'client/rates/rates-simple.html'

    def get_context_data(self, instances):
        data = RatesSerializer(instance=instances, many=True).data
        return {'result': data}

    def get(self, response, name='p'):
        instances = self.model.objects.filter(rtype__name=name).order_by('-date_in')
        context = self.get_context_data(instances)
        return self.render_to_response(context)


class RatesPhysicalView(RatesView):
    template_name = 'client/rates/rates.html'
