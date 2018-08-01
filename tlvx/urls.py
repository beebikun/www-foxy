# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from tlvx import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf.urls.static import static
admin.autodiscover()

from tlvx.views import (
    static_page,
    about,
    rates,
    payment,
    letsfox
)

urlpatterns = [
    ###############################
    ########Служебнные страницы
    ###############################

    url(r'^admin/', include(admin.site.urls)),  # admin site
    url(r'^api/', include('tlvx.api.urls'), name='api'),
    url(r"", include("django.contrib.staticfiles.urls")),

    url(r'^map/?$', static_page.MapPageView.as_view()),


    url(r'^/?$', static_page.IndexPageView.as_view(), name='client-index'),

    ###############################
    ########Menu sections
    ###############################

    ###############################
    # Подключиться

    url(r'^letsfox/?$', letsfox.LetsFoxView.as_view(), name='client-letsfox'),

    ###############################
    # Новости

    url(r'^news/?$', static_page.NewsPageView.as_view(), name='client-news'),
    url(r'^news/(?P<pk>\d+)/$', static_page.NewsDetailPageView.as_view(), name='client-newsdetail'),

    ###############################
    # Интернет -см static page

    ###############################
    # Тарифы

    url(r'^rates/?$', rates.RatesPhysicalView.as_view(), name='client-rates'),
    url(r'^rates/action/?$', rates.RatesActionView.as_view(), name='client-ratesaction'),
    url(r'^rates/other/$', rates.RatesView.as_view(), kwargs={'name': 'other'}, name='client-ratessimple'),

    ###############################
    # Оплата услуг

    url(r'^payment/?$', payment.PaymentChoosePageView.as_view(), name='client-payment'),
    url(r'^payment/card/?$', payment.PaymentCardsPageView.as_view(), name='client-paymentcard'),
    url(r'^payment/elmoney/?$', payment.PaymentElectronicPageView.as_view(), name='client-paymentelmoney'),
    url(r'^payment/limit/?$', payment.PaymentLimitPageView.as_view(), name='client-paymentlimit'),
    url(r'^payment/terminal/?$', payment.PaymentTerminalsPageView.as_view(), name='client-paymentterminal'),

    ###############################
    # О компании

    url(r'^about/?$', about.AboutPageView.as_view(), name='client-about'),
    #url(r'^documents/?$', about.DocumentsPageView.as_view(), name='client-documents'),
    url(r'^vacancy/?$', about.VacancyPageView.as_view(), name='client-vacancy'),

    ###############################
    # Справка

    url(r'^how/?$', static_page.HelpPageView.as_view(), name='client-faq'),

    ###############################
    ######## Static pages
    ###############################

    url(r'^page/(?P<page>[\w-]+)?$', static_page.StaticPageView.as_view(), name='client-simple_content'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
