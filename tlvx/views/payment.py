# -*- coding: utf-8 -*-
from django.views.generic import TemplateView

from tlvx.core.models import StaticPage, Payment


class PaymentChoosePageView(TemplateView):
    """ Выбор типа платежа """
    template_name = "client/payment/payment.html"


class PaymentLimitPageView(TemplateView):
    """Взятие лимита"""
    template_name = "client/payment/payment-limit.html"

    def get(self, *args, **kwargs):
        context = {
            'page': StaticPage.objects.get(name='payment-limit')
        }
        return self.render_to_response(context)


class PaymentElectronicPageView(TemplateView):
    """Эл деньги (Асист)"""
    template_name = "client/payment/payment-elmoney.html"

    def get(self, *args, **kwargs):
        context = {
            'instruction': StaticPage.objects.get(name='asist-instruction'),
            'returns': StaticPage.objects.get(name='asist-returns'),
            'inner': StaticPage.objects.get(name='payment-elmoney-inn'),
        }
        return self.render_to_response(context)


class PaymentCardsPageView(TemplateView):
    """ Оплата картами через ДВпей, сбербанк онлайн и телебанк втб24 """
    template_name = "client/payment/payment-card.html"

    def get(self, *args, **kwargs):
        # @TODO add some latinic `name` to payment model
        context = {
            #'dvpay': Payment.objects.get(pk=9),
            'sberbank': Payment.objects.get(pk=8),
            'telebank': Payment.objects.get(pk=7),
        }
        return self.render_to_response(context)


class PaymentTerminalsPageView(TemplateView):
    template_name = "client/payment/payment-terminal.html"

    def get(self, *args, **kwargs):
        context = {
            'payments': Payment.objects.filter(is_terminal=True),
        }
        return self.render_to_response(context)
