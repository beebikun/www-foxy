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
        context['current_rates_start'] = datetime.datetime(year=2018, month=12, day=1)
        context['current_rates'] = [
            # {
            #     'name': u'Старт', 'payment': '349',
            #     'speed': '5',
            #     'class': 'navy',
            #     'tv_count': context['tv_count'],
            #     'header_href': 'http://tlvx.ru/page/akcii',
            # },
            {
                'name': u'Квартал', 'payment': '549',
                'speed': '50',
                'class': 'navy',
                'tv_count': context['tv_count'],
                'header_href': 'http://tlvx.ru/page/kvartal',
            },
            {
                'name': u'Эталон', 'payment': '599',
                'speed': '30',
                'class': 'navy',
                'tv_count': context['tv_count'],
                'header_href': 'http://tlvx.ru/page/etalon',
            },
            {'name': 'clearfix'},
            {
                'name': u'Стандарт', 'payment': '690',
                'speed': '50',
                'class': 'default',
                'tv_count': context['tv_count'],
            },

            {
                'name': u'Комфорт', 'payment': '990',
                'speed': '60',
                'class': 'default',
                'tv_count': context['tv_count'],
            },

            {
                'name': u'Престиж', 'payment': '1490',
                'speed': '100',
                'class': 'default',
                'tv_count': context['televoxtv_tv_count'],
            },
            {'name': 'clearfix'},
            {
                'name': u'Ежедневник', 'payment': '50',
                'day_speed': '5',
                'class': 'purple',
                'href': 'http://tlvx.ru/page/everyday',
                'dayly': True,
            },
            {
                'name': u'Телевокс ТВ', 'payment': '500',
                'href': 'http://tlvx.ru/page/iptv#televoxtv',
                'tv_count': context['televoxtv_tv_count'],
                'class': 'purple',
                'televoxtv': True,
            },
            {
                'name': u'Всё включено', 'payment': '900',
                'day_speed': '40',
                'class': 'purple',
                'tv_count': context['televoxtv_tv_count'],
                'href': 'http://tlvx.ru/page/allinclude_rate',
            },
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
