# -*- coding: utf-8 -*-
from rest_framework import permissions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from tlvx.api import bg
from tlvx.api import response as project_api_response
from tlvx.api import serializers, forms
from tlvx.core import models


class InvalidRequestException(Exception):

    def __init__(self, errors):
        self.errors = errors


class ProjectApiView(APIView):
    """
        Base class for Lebowsky Web API views
    """

    def handle_exception(self, exc):
        if isinstance(exc, InvalidRequestException):
            return project_api_response.Response(
                self.request_form_errors, status=status.HTTP_400_BAD_REQUEST)
        base_response = APIView.handle_exception(self, exc)
        return project_api_response.Response(
            base_response.data, status=base_response.status_code)

    def validate_and_get_params(self, form_class, data=None, files=None):
        request_form = form_class(data=data, files=files)
        if request_form.is_valid():
            return request_form.cleaned_data
        else:
            self.request_form_errors = request_form.errors
            raise InvalidRequestException(request_form.errors)


class ApiRoot(ProjectApiView):
    def get(self, request, format=None):
        return project_api_response.Response({
            'markers-icons': reverse('markers-icons', request=request),
        })


class MarkerIconsRoot(ApiRoot):
    def get_object(self):
        return models.MarkerIcon.objects.all()

    def get_data(self, obj, request):
        data = serializers.MarkerIconSerializer(instance=obj).data
        root_url = reverse('client-index', request=request)
        data['path'] = obj.get_absolute_url(root_url)
        return data

    def get(self, request, format=None):
        objects = self.get_object()
        data = [self.get_data(obj, request) for obj in objects]
        return project_api_response.Response(data)


class BGLimitRoot(ApiRoot):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        #By some reasons, needed params in params, but forms say other :/
        #So i set requres False for params in form
        params = self.validate_and_get_params(
            forms.BGLimitForm, request.POST)
        message = bg.take_limit(**params)
        return project_api_response.Response({'message': message})
