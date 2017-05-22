# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from django.utils import timezone

from rest_framework import serializers
import math

from tlvx.core.models import StaticPage, HelpPage, Note, Image


class StaticPageSerializer(serializers.ModelSerializer):
    # @TODO: get rid off all serializers
    attach = serializers.Field(source='get_url_attach')

    class Meta:
        model = StaticPage
        fields = (
            'name',
            'content',
            'display_name',
            'attach',
        )


class StaticPageView(DetailView):
    template_name = "client/simple-content.html"
    model = StaticPage
    page_name = None

    def get_context_data(self, instance):
        data = StaticPageSerializer(instance=instance).data
        childs = instance.get_childs()
        data['childs'] = map(self.get_context_data, childs)
        return data

    def get(self, request, **kwargs):
        instance = get_object_or_404(self.model, name=kwargs.get('page', self.page_name))
        context = self.get_context_data(instance)
        return self.render_to_response(context)


class HelpPageView(StaticPageView):
    template_name = "client/how/how.html"
    page_name = 'how'
    model = HelpPage


class MapPageView(TemplateView):
    template_name = "client/map.html"


class NewsPageView(TemplateView):
    template_name = "client/news.html"
    count = 10

    def get_news(self):
        return Note.objects.filter(date__lte=timezone.now()).order_by('-num', '-date')

    def get(self, request):
        notes = self.get_news()
        page_num = int(request.GET.get('page') or 1)
        first = self.count * (page_num - 1)
        end = self.count * page_num

        context = {
            'notes': notes[first:end],
            'max_page': int(math.ceil(notes.count() / float(self.count))),
        }
        return self.render_to_response(context)


class NewsDetailPageView(NewsPageView):
    def get(self, request, pk=None):
        context = {
            'notes': Note.objects.filter(pk=pk)
        }
        return self.render_to_response(context)


class IndexPageView(NewsPageView):
    template_name = "client/index.html"

    def get(self, request, **kwargs):
        context = {
            'notes': self.get_news()[:3],
            'banners': Image.objects.filter(is_displ=True).order_by('num'),
        }
        return self.render_to_response(context)
