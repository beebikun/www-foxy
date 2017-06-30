# -*- coding: utf-8 -*-
from django.views.generic import TemplateView

from tlvx.core.models import Rates, StaticPage


class RatesView(TemplateView):
    template_name = 'client/rates/rates-simple.html'

    def get(self, response, name='p'):
        context = {
            'result': Rates.objects.filter(rtype__name=name).order_by('-date_in'),
            'tv_count': StaticPage.objects.get(name='tv_count').display_name,
            'televoxtv_tv_count': StaticPage.objects.get(name='televoxtv_tv_count').display_name,
        }
        return self.render_to_response(context)


class RatesPhysicalView(RatesView):
    template_name = 'client/rates/rates.html'
