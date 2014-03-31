# -*- coding: utf-8 -*-
"""
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from tlvx.tests import MainTest
from tlvx.api import views as api_views
from tlvx.core import models
from tlvx.helpers import change_keyboard


VARS = lambda i: [i, i.upper(), i.lower(), change_keyboard(i)]

API = {
    'street': 'api/street/',
    'buildings': 'api/buildings/search/',
    'captcha': 'api/captcha/',
    'doit': 'api/doit/'
}


class StreetTestMain(MainTest):
    def setUp(self):
        self.name = u'Ленина'
        self.street_1 = models.Street.objects.get_or_create(name=self.name)[0]
        self.name_sec = u'Варенина'
        self.street_2 = models.Street.objects.get_or_create(
            name=self.name_sec)[0]
        self.pattern_uniq = u'Лен'
        self.pattern_both = u'нина'

    def _get_response(self, response):
        self.assertEqual(
            response.status_code, 200, msg=response.render())
        return self.get_data(response)


class StreetRootTest(StreetTestMain):
    def _get_response(self, key):
        response = self.get_response(API['street'], 'get',
                                     api_views.StreetRoot,
                                     query=dict(name=key))
        return super(StreetRootTest, self)._get_response(response)

    def _test(self, k, e):
        e = map(lambda s: dict(name=s.name, id=s.id), e)
        for key in VARS(k):
            data = self._get_response(k)
            self.assertEqual(data, e)

    def test_search(self):
        keys = [self.name, self.pattern_uniq, ]
        for key in keys:
            self._test(k=key, e=[self.street_1])

    def test_by_pattern_both(self):
        self._test(k=self.pattern_both, e=[self.street_1, self.street_2])


class BuildingSearchTest(StreetTestMain):
    def setUp(self):
        def create_b(params):
            params['lat'] = 1.0
            params['lng'] = 1.0
            return models.Building.objects.get_or_create(**params)[0]
        super(BuildingSearchTest, self).setUp()
        num_1 = '111'
        num_1_alt = '222'
        num_2 = '11'
        num_3 = '22'
        self.building_1 = create_b(
            dict(num=num_1, street=self.street_1,
                 num_alt=num_1_alt, street_alt=self.street_2, active=True))
        self.building_2 = create_b(
            dict(num=num_2, street=self.street_1, active=True))
        self.building_3 = create_b(dict(num=num_3, street=self.street_2))

    def _get_response(self, num, street):
        response = self.get_response(API['buildings'], 'get',
                                     api_views.BuildingSearch,
                                     query=dict(num=num, street=street))
        return super(BuildingSearchTest, self)._get_response(response)

    def _test(self, num, street, result, simular=[]):
        ser = lambda b: dict(street=b.street.name, name=None, id=b.id,
                             address=b.get_address(), active=b.active,
                             num=b.num, plan=b.plan, lat=1.0, co=None, lng=1.0)
        if result:
            result = ser(result)
        simular = map(ser, simular)
        for s in VARS(street):
            for n in VARS(num):
                data = self._get_response(n, s)
                self.assertEqual(data.get('result'), result, msg=[s, n])
                self.assertEqual(data.get('simular'), simular, msg=[s, n])

    def test_search(self):
        r = self.building_1
        #stright test - should return only this b
        self._test(num=self.building_1.num,
                   street=self.building_1.street.name,
                   result=r)
        # test by alt address - should return only this b
        self._test(num=self.building_1.num_alt,
                   street=self.building_1.street_alt.name,
                   result=r)
        #test by simular address
        self._test(num=self.building_2.num,
                   street=self.building_2.street.name,
                   result=self.building_2, simular=[self.building_1])
        self._test(num=self.building_3.num,
                   street=self.building_3.street.name,
                   result=self.building_3, simular=[self.building_1])


class CaptchaTest(MainTest):
    pass


class DGisTest(MainTest):
    pass


class ConnRequestTest(MainTest):
    pass
