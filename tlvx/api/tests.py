# -*- coding: utf-8 -*-
"""
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import json
from django.test import TestCase
from django.test.client import RequestFactory
from tlvx.api import views as api_views
from tlvx.core import models


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
        if hasattr(views, 'as_view'):
            views = views.as_view()
        return views(request, **kwargs)

# API TESTS

API = {
    'street': 'api/street/',
    'building': 'api/buildings/search/',
    'captcha': 'api/captcha/',
    'doit': 'api/doit/'
}


class StreetTestMain(MainTest):
    def setUp(self):
        self.name = u'Ленина'
        models.Street.objects.get_or_create(name=self.name)
        self.name_sec = u'Варенина'
        models.Street.objects.get_or_create(name=self.name_sec)
        self.pattern_uniq = u'Лен'
        self.pattern_both = u'нина'
        self.wrong_set = 'Ktybyf'


class StreetRootTest(StreetTestMain):
    def _get_response(self, key):
        response = self.get_response(
            API['street'], 'get', api_views.StreetRoot, query=dict(name=key))
        self.assertEqual(
            response.status_code, 200, msg=response.render())
        return self.get_data(response)

    def _get_expectation(self, names):
        if isinstance(names, basestring):
            names = [names]
        return map(
            lambda n: dict(name=n, id=models.Street.objects.get(name=n).id),
            names)

    def _test(self, k, names):
        e = self._get_expectation(names)
        keys = [k, k.upper(), k.lower()]
        for key in keys:
            data = self._get_response(k)
            self.assertEqual(data, e)

    def test_search(self):
        keys = [self.name, self.wrong_set, self.pattern_uniq, ]
        for key in keys:
            self._test(k=key, names=self.name)

    def test_by_pattern_both(self):
        self._test(k=self.pattern_both, names=[self.name, self.name_sec])


class BuildingSearchTest(MainTest):
    pass


class TestCaptcha(MainTest):
    pass


class Test2Gis(MainTest):
    pass
