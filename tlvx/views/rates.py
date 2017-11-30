# -*- coding: utf-8 -*-
import datetime
from django.views.generic import TemplateView

from tlvx.core.models import Rates, StaticPage


class RatesView(TemplateView):
    template_name = 'client/rates/rates-simple.html'

    def tv_count(self):
        return StaticPage.objects.get(name='tv_count').display_name

    def televoxtv_tv_count(self):
        return StaticPage.objects.get(name='televoxtv_tv_count').display_name

    def get_context(self, name):
        return {
            'result': Rates.objects.filter(rtype__name=name).order_by('-date_in'),
            'tv_count': self.tv_count,
            'televoxtv_tv_count': self.televoxtv_tv_count,
        }

    def get(self, response, name='p'):
        context = self.get_context(name)
        return self.render_to_response(context)


class RatesPhysicalView(RatesView):
    template_name = 'client/rates/rates.html'

    def get_context(self, name):
        context = super(RatesPhysicalView, self).get_context(name)
        context['current_rates_start'] = datetime.datetime(year=2017, month=12, day=1)
        context['current_rates'] = [
            {'name': u'Всё включено', 'payment': '900', 'day_speed': '30',
             'tv_count': context['televoxtv_tv_count'], 'class': 'navy',
             'href': 'http://tlvx.ru/page/allinclude_rate', },

            {'name': u'Стандарт', 'payment': '690', 'speed': '40',
             'tv_count': context['tv_count'], 'class': 'default', },

            {'name': u'Комфорт', 'payment': '990', 'speed': '50',
             'tv_count': context['tv_count'], 'class': 'default', },

            {'name': 'clearfix'},

            {'name': u'Престиж', 'payment': '1490', 'speed': '90',
             'tv_count': context['tv_count'], 'class': 'default', },

            {'name': u'Телевокс ТВ', 'payment': '500',
             'tv_count': context['televoxtv_tv_count'], 'class': 'navy',
             'televoxtv': True,
             'href': 'http://tlvx.ru/page/iptv#televoxtv', },
        ]
        return context


class RatesActionView(RatesView):
    template_name = 'client/rates/rates.html'

    def get_context(self, name):
        context = {
            'tv_count': self.tv_count,
            'televoxtv_tv_count': self.televoxtv_tv_count,
            'result': [{'active': True}]
        }
        context['current_rates_start'] = datetime.datetime(year=2017, month=7, day=1)
        context['current_rates'] = [

            {'name': u'Летний', 'payment': '650',
             'tv_count': context['tv_count'], 'class': 'navy lg summer',
             'summer': True,
             'href': 'http://tlvx.ru/page/rate-summer', },

            {'name': u'Телевокс ТВ+', 'payment': '250',
             'tv_count': context['televoxtv_tv_count'], 'class': 'navy lg',
             'televoxtv': True,
             'href': 'http://tlvx.ru/page/televoxtv-plus', },
        ]
        return context
