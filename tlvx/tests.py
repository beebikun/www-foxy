# -*- coding: utf-8 -*-
import json
from django.test import TestCase
from django.test.client import RequestFactory
from tlvx import helpers, settings, views as tlvx_views


class MainTest(TestCase):
    def get_data(self, response):
        content = json.loads(response.render().content)
        return content.get('data') if isinstance(content, dict) else content

    def get_response(self, path, method, views,
                     query=None, data=None, user=None, kwargs=None):
        """Generate request.

        Args:
            path - path for request, str.
            method - method for request, str.
            views - str,
            normal_code - expected code, num.
            query - query for request, dict
            data - data for request, dict
            user - <User> instance
            files - dict, for ex
                {"photo": SHORT_PATH} or {"photo": PHOTO_FILE}
            kwargs - dict

        Returns:
            response
        """
        factory = RequestFactory()
        request = getattr(factory, method.lower())(path)
        request._dont_enforce_csrf_checks = True
        if data:
            request.POST.update(**data)
        if query:
            request.GET = query
        if user:
            request.user = user
        if not kwargs:
            kwargs = {}
        if hasattr(views, 'as_view'):  # as_view - rest_framework views
            views = views.as_view()
        return views(request, **kwargs)


class SimpleTest(MainTest):
    def setUp(self):
        self.data4test = []
        self.fn = lambda data: None

    def test_fn(self):
        for data, result in self.data4test:
            _is = self.fn(data)
            self.assertEqual(
                _is, result, msg="%s - %s != %s" % (data, _is, result))


class ChangeKeyboardTest(SimpleTest):
    def setUp(self):
        self.data4test = [
            (u'Ленина', u'Ленина'),
            (u'Ktybyf', u'Ленина'),
            (u',erf', u'бука'),
            (u',ука', u',ука'),
            (u',zка', u'бяка'),
            (u'.erf', u'юука'),
            (u'.ука', u'.ука'),
            (u'.zка', u'юяка'),
        ]
        self.fn = helpers.change_keyboard


class IsGrayIpTest(SimpleTest):
    def setUp(self):
        self.data4test = [
            ('a.1.1.1', None),  # wrong ip
            ('10.0.0.0', True),  # 10.0.0.0/8
            ('10.255.255.255', True),  # 10.0.0.0/8
            ('172.16.0.0', True),  # 172.16.0.0/14
            ('172.31.255.255', True),  # 172.16.0.0/14
            ('192.168.0.0', True),  # 192.168.0.0/16
            ('192.168.255.255', True),  # 192.168.0.0/16
            ('1.1.1.1', False),  #
        ]
        self.fn = tlvx_views.is_gray_ip


class PaginatorTest(SimpleTest):
    def setUp(self):
        p = settings.PAGINATOR_PAGE - 4
        count = p*10
        half = (p - 1)/2
        empty = ['...']
        _strt_e = [1] + empty
        _end_e = empty + [count]
        start = range(1, p+1) + _end_e   # <-(1)(2)(3)(...)(LAST)->
        middle = lambda c: _strt_e + range(c - half, c + half + 1) \
            + _end_e  # <-(1)(...)(10)(11)(12)(...)(53)->
        end = _strt_e + range(count - p + 1, count + 1)  # <-(1)(..)(7)(8)(9)->
        self.data4test = [
            (1, start),
            (int(p/2) + 1, start),
            (p-1, start),
            (p, middle(p)),
            (p*2, middle(p*2)),
            (count - p, middle(count - p)),
            (count - p + 1, middle(count - p + 1)),
            (count - p + 2, end),
            (count - int(p/2) - 1, end),
            (count, end),
        ]
        self.fn = lambda cur: tlvx_views.paginator(count, cur)


class IndexTest(SimpleTest):
    def setUp(self):
        self.data4test = []
        self.fn = lambda i: None
