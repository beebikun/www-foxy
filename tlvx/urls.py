# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from tlvx import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/',  include(admin.site.urls)),  # admin site
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^api/', include('tlvx.api.urls'), name='api'),
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT,
        }),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.STATIC_URL,
        }),
    url(r'^client/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.CLIENT_ROOT,
        }),

    url(r'^map?$', 'tlvx.views.map_page'),

    url(r'^/?$', 'tlvx.views.index', name='client-index'),
    url(r'^!/?$', 'tlvx.views.index'),

    #Menu sections

    #Подключиться
    url(r'^!/letsfox/?$', 'tlvx.views.letsfox', name='client-letsfox'),

    #Новости
    url(r'^!/news/?$', 'tlvx.views.news', name='client-news'),
    url(r'^!/news/(?P<pk>\d+)/$', 'tlvx.views.news', name='client-newsdetail'),

    #Интернет -см static page

    #Тарифы
    url(r'^!/rates/?$', 'tlvx.views.rates', name='client-rates'),
    url(r'^!/rates/(?P<name>\w+)/$', 'tlvx.views.rates_simple',
        name='client-ratessimple'),

    #Оплата услуг
    url(r'^!/payment/?$', 'tlvx.views.payment', name='client-payment'),
    url(r'^!/payment/card/?$', 'tlvx.views.paymentcard',
        name='client-paymentcard'),
    # url(r'^!/payment/limit/?$', 'tlvx.views.paymentlimit', name='client-paymentlimit'),
    url(r'^!/payment/terminal/?$', 'tlvx.views.paymentterminal',
        name='client-paymentterminal'),
    url(r'^!/payment/mobile/?$',
        'tlvx.views.paymentmobile', name='client-paymentmobile'),
    url(r'^!/payment/(?P<name>\w+)/?$',
        'tlvx.views.payment', name='client-payment'),

    #О компании
    url(r'^!/about/?$', 'tlvx.views.about', name='client-about'),
    url(r'^!/documents/?$', 'tlvx.views.documents', name='client-documents'),
    url(r'^!/vacancy/?$', 'tlvx.views.vacancy', name='client-vacancy'),

    #Справка
    url(r'^!/how/?$', 'tlvx.views.how', name='client-faq'),

    #Static pages
    url(r'^!/(?P<page>[\w-]+)?$', 'tlvx.views.simple_content',
        name='client-simple_content'),
)
