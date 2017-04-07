# -*- coding: utf-8 -*-
from django.views.generic import TemplateView

from tlvx.core.models import DocumentsPage, VacancyPage, CentralOffice
from tlvx.views.static_page import StaticPageView


class AboutPageView(TemplateView):
    template_name = 'client/about/about.html'
    model = CentralOffice

    def get(self, request, **kwargs):
        context = {
            'offices': CentralOffice.objects.filter(in_map=True),
        }
        return self.render_to_response(context)


class DocumentsPageView(StaticPageView):
    template_name = 'client/about/documents.html'
    model = DocumentsPage


class VacancyPageView(StaticPageView):
    template_name = 'client/about/vacancy.html'
    model = VacancyPage
