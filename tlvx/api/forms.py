# -*- coding: utf-8 -*-
from django import forms
from tlvx import settings


class BuildingsDetailRequestForm(forms.Form):
    street = forms.CharField(required=True, label=u'Запрос')
    num = forms.CharField(required=False, label=u'Номер дома')


class StreetRequestForm(forms.Form):
    name = forms.CharField(required=True, label=u'')


class NoteRequestForm(forms.Form):
    page = forms.IntegerField(required=False, label=u'Страницы', initial=1)
    count = forms.IntegerField(required=False, label=u'Элементов на странице',
                               initial=settings.NOTE_COUNT)


class BGLimitForm(forms.Form):
    pswd = forms.CharField(required=False, label=u'Номер договора')
    user = forms.CharField(required=False, label=u'Пароль')


class NewsRequestForm(forms.Form):
    page = forms.IntegerField(required=False, label=u'')
    pk = forms.IntegerField(required=False, label=u'')
