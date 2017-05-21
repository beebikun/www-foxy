# -*- coding: utf-8 -*-
from rest_framework import serializers


class MarkerIconSerializer(serializers.Serializer):
    id = serializers.Field()
    name = serializers.CharField(read_only=True)
    path = serializers.CharField(read_only=True, source="get_absolute_url")
    width = serializers.IntegerField(read_only=True)
    height = serializers.IntegerField(read_only=True)
