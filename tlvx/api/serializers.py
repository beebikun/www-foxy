# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from tlvx.core import models
from tlvx.helpers import change_keyboard

# class BuildingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.Building

# class StreetSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.Street


class BuildingSerializer(serializers.Serializer):
    id = serializers.Field()
    num = serializers.CharField(required=True)
    street = serializers.ChoiceField(required=True, choices=[
        (street.pk, street.pk) for street in models.Street.objects.all()
    ])
    address = serializers.CharField(required=False, source='get_address')
    lat = serializers.FloatField(required=False)
    lng = serializers.FloatField(required=False)
    name = serializers.CharField(required=False)
    active = serializers.BooleanField(required=False)
    plan = serializers.BooleanField(required=False)
    # co = serializers.Field(source=co)

    def validate(self, attrs):
        # attrs = super(BuildingSerializer, self).validate(attrs)
        clear_num = lambda num: num.lower().replace(' ', '')
        num = change_keyboard(attrs.get('num'))
        street = attrs.get('street')
        model = models.Building.objects
        building_list = filter(lambda b: clear_num(b.num) == clear_num(num),
                               model.filter(street__id=street)) or \
            filter(lambda b: clear_num(b.num_alt) == clear_num(num),
                   model.filter(street_alt__id=street))
        try:
            building = building_list[0] if building_list else model.create(
                num=num, street_id=street)
        except FieldError, e:
            raise serializers.ValidationError(_(e.args[0]))
        return building


class StreetSerializer(serializers.Serializer):
    id = serializers.Field()
    name = serializers.CharField(required=True)

    def validate(self, attrs):
        attrs = super(StreetSerializer, self).validate(attrs)
        name = attrs.get('name')
        n = name.lower()
        streets = filter(
            lambda s: (s.name.lower() == n) or (
                change_keyboard(s.name.lower()) == n),
            models.Street.objects.all())
        if not streets:
            raise serializers.ValidationError(_(
                "Street with name %s is not create in db" % (name)))
        return streets[0]



class NoteSerializer(serializers.Serializer):
    id = serializers.Field()
    header = serializers.CharField(required=False)
    text = serializers.Field()
    date = serializers.IntegerField(required=False)
    ntype = serializers.Field()


class DoitSerializer(serializers.Serializer):
    fio = serializers.CharField(
        required=True, max_length=128,
        error_messages=dict(required=u"Пожалуйста, укажите своё имя"))
    phone = serializers.CharField(
        required=False, max_length=128,)
    email = serializers.EmailField(
        required=False, max_length=128,
        error_messages={'invalid': u'Извините, но это не похоже на e-mail'})
    flat = serializers.CharField(required=False, max_length=128)
    address = serializers.CharField(required=True)
    status = serializers.CharField(required=True)
    is_action = serializers.BooleanField(required=False)
    source = serializers.CharField(required=False, max_length=512)
    comment = serializers.CharField(required=False, max_length=512)
    captcha_key = serializers.CharField(required=True, max_length=64)
    captcha = serializers.CharField(required=False, max_length=64)

    def _validate_email_and_phone(self, attrs, source):
        if not attrs.get('email') and not attrs.get('phone'):
            raise serializers.ValidationError(
                u"Укажите либо телефон, либо электронный адрес")
        return attrs

    def validate_email(self, attrs, source):
        return self._validate_email_and_phone(attrs, source)

    def validate_phone(self, attrs, source):
        return self._validate_email_and_phone(attrs, source)

    def validate_captcha(self, attrs, source):
        captcha = attrs.get(source)
        if not captcha:
            raise serializers.ValidationError(u"Вы не выбрали логотип.")
        else:
            captcha_obj = models.CaptchaImageClone.objects.get(img=captcha)
            models.CaptchaImageClone.objects.filter(
                key=attrs['captcha_key']).delete()
            if not captcha_obj.right:
                raise serializers.ValidationError(
                    u"Вы выбрали неверный логотип :(. Попробуйте еще раз")
        del(attrs[source])
        return attrs

    def validate(self, attrs):
        attrs = super(DoitSerializer, self).validate(attrs)
        return attrs

    def restore_object(self, attrs, instance=None):
        """
        Given a dictionary of deserialized field values, either update
        an existing model instance, or create a new model instance.
        """
        del attrs['captcha_key']
        request = models.ConnRequest.objects.create(**attrs)
        models.ConnRequest.objects.sendAll()
        return request


class MarkerIconSerializer(serializers.Serializer):
    id = serializers.Field()
    name = serializers.CharField(required=False)
    path = serializers.CharField(required=False, source="get_absolute_url")
    width = serializers.IntegerField(required=False, source="width")
    height = serializers.IntegerField(required=False, source="height")

