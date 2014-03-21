# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist, FieldError
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


class PaymentSerializer(serializers.Serializer):
    id = serializers.Field()
    name = serializers.CharField(required=True)
    description = serializers.Field()
    marker = serializers.Field()
    hint_line = serializers.Field()

    def validate(self, attrs):
        attrs = super(PaymentSerializer, self).validate(attrs)
        name = attrs.get('name')
        try:
            payment = models.Payment.objects.get(name=name)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(_(
                "Payment with name %s is not create in db" % (name)))
        return payment


class PaymentPointSerializer(serializers.Serializer):
    id = serializers.Field()
    name = serializers.CharField(required=False)
    schedule = serializers.CharField(required=False)
    contacts = serializers.CharField(required=False)
    lat = serializers.FloatField(required=False, source="lat")
    lng = serializers.FloatField(required=False, source="lng")
    address = serializers.CharField(required=False, source="get_address")

    def validate(self, attrs):
        attrs = super(PaymentPointSerializer, self).validate(attrs)
        pk = attrs.get('id')
        try:
            point = models.PaymentPoint.objects.get(id=pk)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(_(
                "PaymentPoint with pk %s is not create in db" % (pk)))
        return point


class RatesSerializer(serializers.Serializer):
    id = serializers.Field()
    name = serializers.CharField(required=False)
    tables = serializers.Field()
    active = serializers.BooleanField(required=False)
    date_in = serializers.DateTimeField(required=False)
    date_out = serializers.DateTimeField(required=False)

    def validate(self, attrs):
        attrs = super(RatesSerializer, self).validate(attrs)
        return attrs


class MarkerIconSerializer(serializers.Serializer):
    id = serializers.Field()
    name = serializers.CharField(required=False)
    path = serializers.CharField(required=False, source="get_absolute_url")
    width = serializers.IntegerField(required=False, source="width")
    height = serializers.IntegerField(required=False, source="height")


class NoteSerializer(serializers.Serializer):
    id = serializers.Field()
    header = serializers.CharField(required=False)
    text = serializers.Field()
    date = serializers.IntegerField(required=False)
    ntype = serializers.Field()


class StaticPageSerializer(serializers.Serializer):
    id = serializers.Field()
    name = serializers.CharField(required=True)
    content = serializers.Field()
    display_name = serializers.CharField(required=False)
    childs = serializers.Field(source='get_child')
    attach = serializers.Field(source='get_url_attach')

    def validate(self, attrs):
        attrs = super(StaticPageSerializer, self).validate(attrs)
        name = attrs.get('name')
        try:
            page = models.StaticPage.objects.get(name=name)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(_(
                "StaticPage with name %s is not create in db" % (name)))
        return page


class DoitSerializer(serializers.Serializer):
    fio = serializers.CharField(required=False, max_length=128)
    phone = serializers.CharField(required=False, max_length=128)
    email = serializers.EmailField(required=False, max_length=128)
    flat = serializers.CharField(required=False, max_length=128)
    address = serializers.CharField(required=True)
    source = serializers.CharField(required=False, max_length=512)
    comment = serializers.CharField(required=False, max_length=512)
    captcha_key = serializers.CharField(required=True, max_length=64)
    captcha = serializers.CharField(required=False, max_length=64)

    def validate_fio(self, attrs, source):
        if not attrs.get(source):
            raise serializers.ValidationError(u"Пожалуйста, укажите своё имя")
        return attrs

    def validate_flat(self, attrs, source):
        if not attrs.get(source):
            raise serializers.ValidationError(
                u"Пожалуйста, укажите номер квартиры")
        return attrs

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
        if instance is not None:
            return instance
        r = models.ConnRequest.objects.create(**attrs)
        return r


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Image
