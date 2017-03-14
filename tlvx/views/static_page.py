# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView
from rest_framework import serializers

from tlvx.core.models import StaticPage, HelpPage


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

    def get_context_data(self, instance):
        data = StaticPageSerializer(instance=instance).data
        childs = instance.get_childs()
        data['childs'] = map(self.get_context_data, childs)
        return data

    def get(self, request, **kwargs):
        instance = get_object_or_404(self.model, name=kwargs.get('page'))
        context = self.get_context_data(instance)
        return self.render_to_response(context)


# def simple_content(request, page=None):
#     """Для отображения простых static page"""
#     return StaticPageView(request=request).response


class HelpPageView(StaticPageView):
    template_name = "client/how/how.html"
    model = HelpPage
