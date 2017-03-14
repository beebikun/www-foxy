# -*- coding: utf-8 -*-
from django.views.generic.detail import DetailView
from rest_framework import serializers

from tlvx.core.models import DocumentsPage, VacancyPage, CentralOffice
from tlvx.views.static_page import StaticPageView


class COSerializer(serializers.ModelSerializer):
    ico = serializers.Field(source='marker.name')
    address = serializers.Field(source='address.get_address')

    class Meta:
        model = CentralOffice


class AboutPageView(DetailView):
    template_name = 'client/about/about.html'
    model = CentralOffice

    def get(self, request, **kwargs):
        offices = CentralOffice.objects.filter(in_map=True)
        data = COSerializer(instance=offices, many=True).data
        return self.render_to_response({'offices': data})


class DocumentsPageView(StaticPageView):
    template_name = 'client/about/documents.html'
    model = DocumentsPage


class VacancyPageView(StaticPageView):
    template_name = 'client/about/vacancy.html'
    model = VacancyPage
