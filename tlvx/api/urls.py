# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from tlvx.api import views as root


urlpatterns = patterns(
    '',
    # url(r'^$', root.ApiRoot.as_view()),
    url(r'^buildings/search/?$',
        root.BuildingSearch.as_view(), name='building-search'),
    url(r'^street/?$', root.StreetRoot.as_view(), name='street'),
    url(r'^news/?$', root.NewsRoot.as_view(), name='news'),
    url(r'^markers-icons/?$',
        root.MarkerIconsRoot.as_view(), name='markers-icons'),
    url(r'^captcha/?$', root.CaptchaRoot.as_view(), name='captcha'),
    url(r'^doit/?$', root.DoitRoot.as_view(), name='doit'),
    url(r'^bg/limit?$', root.BGLimitRoot.as_view(), name='bg-limit'),
)
