# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from tlvx import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from tlvx.views import (
    static_page,
    about,
    rates,
    payment,
)

urlpatterns = patterns(
    '',
    ###############################
    ########Служебнные страницы
    ###############################

    url(r'^admin/', include(admin.site.urls)),  # admin site
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^api/', include('tlvx.api.urls'), name='api'),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT,
        }),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.STATIC_ROOT,
        }),
    # url(r'^client/(?P<path>.*)$', 'django.views.static.serve', {
    #     'document_root': settings.CLIENT_ROOT,
    #     }),

    url(r'^map?$', 'tlvx.views.map_page'),


    url(r'^/?$', 'tlvx.views.index', name='client-index'),
    url(r'^!/?$', 'tlvx.views.index'),

    ###############################
    ########Menu sections
    ###############################

    ###############################
    # Подключиться

    url(r'^!/letsfox/?$', 'tlvx.views.letsfox', name='client-letsfox'),

    ###############################
    # Новости

    url(r'^!/news/?$', 'tlvx.views.news', name='client-news'),
    url(r'^!/news/(?P<pk>\d+)/$', 'tlvx.views.news', name='client-newsdetail'),

    ###############################
    # Интернет -см static page

    ###############################
    # Тарифы

    url(r'^!/rates/?$', rates.RatesPhysicalView.as_view(), name='client-rates'),
    url(r'^!/rates/(?P<name>\w+)/$', rates.RatesView.as_view(), name='client-ratessimple'),

    ###############################
    # Оплата услуг

    url(r'^!/payment/?$', payment.PaymentChoosePageView.as_view(), name='client-payment'),
    url(r'^!/payment/card/?$', payment.PaymentCardsPageView.as_view(), name='client-paymentcard'),
    url(r'^!/payment/elmoney/?$', payment.PaymentElectronicPageView.as_view(), name='client-paymentelmoney'),
    url(r'^!/payment/limit/?$', payment.PaymentLimitPageView.as_view(), name='client-paymentlimit'),
    url(r'^!/payment/terminal/?$', payment.PaymentTerminalsPageView.as_view(), name='client-paymentterminal'),

    ###############################
    # О компании

    url(r'^!/about/?$', about.AboutPageView.as_view(), name='client-about'),
    url(r'^!/documents/?$', about.DocumentsPageView.as_view(), kwargs={'page': 'documents'}, name='client-documents'),
    url(r'^!/vacancy/?$', about.VacancyPageView.as_view(), kwargs={'page': 'vacancy'}, name='client-vacancy'),

    ###############################
    # Справка

    url(r'^!/how/?$', static_page.HelpPageView.as_view(), kwargs={'page': 'how'}, name='client-faq'),

    ###############################
    ######## Static pages
    ###############################

    url(r'^!/(?P<page>[\w-]+)?$', static_page.StaticPageView.as_view(), name='client-simple_content'),
)
