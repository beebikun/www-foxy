# -*- coding: utf-8 -*-
import random
import uuid
from django.core.files import File
from django.utils import timezone
from rest_framework import permissions
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from tlvx.api import bg
from tlvx.api import response as project_api_response
from tlvx.api import serializers, forms
from tlvx.core import models
from tlvx.helpers import change_keyboard
from tlvx.settings import MEDIA_ROOT


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
            'building-search': reverse('building-search', request=request),
            'street': reverse('street', request=request),
            'markers-icons': reverse('markers-icons', request=request),
            'captcha': reverse('captcha', request=request),
        })


class StreetRoot(ApiRoot):
    def get_object(self, name=''):
        return list(models.Street.objects.filter(name__icontains=name))

    def get_data(self, obj):
        return serializers.StreetSerializer(instance=obj).data

    def get(self, request, format=None,):
        params = self.validate_and_get_params(
            forms.StreetRequestForm, request.QUERY_PARAMS)
        #print change_keyboard(params['name'])
        objects = set(self.get_object(params['name']) +
                      self.get_object(change_keyboard(params['name'])))
        data = [self.get_data(obj) for obj in objects]
        return project_api_response.Response(data)


class BuildingSearch(ApiRoot):
    """
    For example,
    [Building  street u"Кантемирова" num "23"](?street=Кантемирова&num=23)
    """
    models = models.Building.objects

    def filter_objects_simular(self, street, num, result):
        return filter(
            lambda b: b.search_by_address(street=street, num=num),
            models.Building.objects.exclude(id=result and result.id or 0)
            )

    def get_data(self, obj):
        if obj:
            data = serializers.BuildingSerializer(instance=obj).data
            data[u'co'] = obj.co and (obj.co.contacts + ', ' + obj.co.schedule)
        else:
            data = {}
        return data

    def get(self, request, format=None):
        params = self.validate_and_get_params(
            forms.BuildingsDetailRequestForm, request.QUERY_PARAMS)
        serializer = serializers.StreetSerializer(
            data={'name': params['street']})
        if serializer.is_valid():
            serializer = serializers.BuildingSerializer(
                data={'num': params['num'], 'street': serializer.object.pk})
            if serializer.is_valid():
                params['result'] = serializer.object
                data = {
                    'simular': [self.get_data(obj) for obj in
                                self.filter_objects_simular(**params)],
                    'result': self.get_data(params['result'])
                }
                return project_api_response.Response(data)
        return project_api_response.Response(serializer.errors)


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


class DoitRoot(ApiRoot):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        s = serializers.DoitSerializer(data=request.POST)
        if s.is_valid():
            return project_api_response.Response({'doit': True})
        else:
            return project_api_response.Response(s.errors)


class BGLimitRoot(ApiRoot):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        params = self.validate_and_get_params(
            forms.BGLimitForm, request.POST)
        message = bg.take_limit(**params)
        return project_api_response.Response({'message': message})


class CaptchaRoot(ApiRoot):
    model = models.CaptchaImage.objects
    clone_model = models.CaptchaImageClone.objects

    def del_old(self):
        self.clone_model.exclude(
            date__day=timezone.now().day,
            date__month=timezone.now().month,
            date__year=timezone.now().year).delete()

    def get_object(self):
        self.del_old()
        images = list(
            self.model.filter(right=False, key='').order_by('?')[:2])
        images.append(self.model.filter(right=True, key='').order_by('?')[0])
        random.shuffle(images)
        return images

    def get_data(self, orig_obj, key, request):
        new_obj = self.clone_model.create(
            key=key, img=File(open(MEDIA_ROOT+'/'+orig_obj.img.name)),
            right=orig_obj.right)
        root_url = reverse('client-index', request=request)
        return dict(
            src=new_obj.get_absolute_url(root_url),
            name=new_obj.img.name
        )

    def get(self, request, format=None):
        objects = self.get_object()
        key = '%s' % uuid.uuid4()
        data = dict(
            key=key,
            images=[self.get_data(obj, key, request) for obj in objects])
        return project_api_response.Response(data)
