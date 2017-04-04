# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from django.utils import timezone

from rest_framework import serializers

from tlvx.core.models import StaticPage, HelpPage, Note


class StaticPageSerializer(serializers.ModelSerializer):
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

    def _get_static_content(self, name):
        instance = get_object_or_404(self.model, name=name)
        return StaticPageSerializer(instance=instance).data

    def get(self, request, **kwargs):
        instance = get_object_or_404(self.model, name=kwargs.get('page', self.page_name))
        context = self.get_context_data(instance)
        return self.render_to_response(context)


class HelpPageView(StaticPageView):
    template_name = "client/how/how.html"
    model = HelpPage


class MapPageView(TemplateView):
    template_name = "client/map.html"
