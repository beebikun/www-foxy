# -*- coding: utf-8 -*-
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from rest_framework import serializers

from tlvx.views.static_page import StaticPageView
from tlvx.core.models import Payment, PaymentPoint


class PaymentSerializer(serializers.ModelSerializer):
    ico = serializers.Field(source='marker.name')

    class Meta:
        model = Payment


class PaymentPointSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_name')
    address = serializers.CharField(source='address.get_address')
    lat = serializers.FloatField(source='address.lat')
    lng = serializers.FloatField(source='address.lng')

    class Meta:
        model = PaymentPoint
        fields = ('id', 'name', 'lat', 'lng', 'address')

    def get_name(self, instance):
        if instance.name is None:
            return instance.address.get_address()
        return instance.name


class PaymentChoosePageView(TemplateView):
    """ Выбор типа платежа """
    template_name = "client/payment/payment.html"


class PaymentLimitPageView(StaticPageView):
    """Взятие лимита"""
    template_name = "client/payment/payment-limit.html"
    page_name = 'payment-limit'


class PaymentElectronicPageView(StaticPageView):
    """Эл деньги (Асист)"""
    template_name = "client/payment/payment-elmoney.html"

    def get(self, *args, **kwargs):
        context = {
            'instruction': self._get_static_content('asist-instruction'),
            'returns': self._get_static_content('asist-returns'),
            'inner': self._get_static_content('payment-elmoney-inn'),
        }
        return self.render_to_response(context)


class PaymentCardsPageView(DetailView):
    """ Оплата картами через ДВпей, сбербанк онлайн и телебанк втб24 """
    model = Payment
    template_name = "client/payment/payment-card.html"

    def get_context(self, pk):
        instance = Payment.objects.get(pk=pk)
        return PaymentSerializer(instance=instance).data

    def get(self, *args, **kwargs):
        context = {
            'dvpay': self.get_context(9),
            'sberbank': self.get_context(8),
            'telebank': self.get_context(7),
        }
        return self.render_to_response(context)


class PaymentTerminalsPageView(DetailView):
    template_name = "client/payment/payment-terminal.html"
    model = Payment

    def get(self, *args, **kwargs):
        instances = self.model.objects.filter(is_terminal=True)
        payments = []
        for instance in instances:
            data = PaymentSerializer(instance=instance).data
            data['points'] = PaymentPointSerializer(instance=instance.get_points(), many=True).data
            payments.append(data)
        return self.render_to_response({'payments': payments})
