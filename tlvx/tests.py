# -*- coding: utf-8 -*-
from datetime import datetime
import json
import math
import pytz
from random import randint, random, getrandbits
import uuid
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from tlvx import helpers, settings, views as tlvx_views
from tlvx.core import models
from django.core.files.uploadedfile import SimpleUploadedFile


def _stf(length=8):
    n = int(math.ceil(length/8.0))
    s = map(lambda i: str(uuid.uuid4()).split('-')[0], xrange(n))
    return ''.join(s)[:length]


def _rnd_bool():
    return bool(getrandbits(1))


def _random_date():
    return datetime(2014, randint(1, 12), randint(1, 27), tzinfo=pytz.UTC)


def _rnd_obj(modelname, params={}):
    array = getattr(models, modelname).objects.filter(**params)
    return array[randint(0, array.count()-1)] if array.exists() else None


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
        # path = self.urls[pathname]
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


class SimpleTest(TestCase):
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
        self.p = p
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
        self.fn = lambda cur, count=count: tlvx_views.paginator(count, cur)

    def _test_short(self, count):
        def _test((cur, r)):
            _is = self.fn(cur, count)
            self.assertEqual(_is, r, msg="%s/%s - %s != %s" % (
                cur, count, _is, r))

        data4test = [
            (1, range(1, count+1)),
            (int(count/2), range(1, count+1)),
            (count, range(1, count+1)),
        ]
        map(_test, data4test)

    def test_short(self):
        self._test_short(int(self.p/2))
        self._test_short(int(self.p/2)+1)
        self._test_short(self.p - 1)
        self._test_short(1)
        self._test_short(2)


class ViewsMainTest(TestCase):
    def _get(self, name, kwargs={}, query=None):
        def _get_data(context):
            for c in context:
                if 'data' in c:
                    return c['data']
                if isinstance(c, (list, dict)):
                    return _get_data(c)
            return
        query = '?' + '&'.join(
            ['%s=%s' % (k, v) for k, v in query.iteritems()]) if query else ''
        response = self.client.get(reverse(name, kwargs=kwargs) + query)
        data = _get_data(response.context)
        self.assertTrue(data, msg="No data for %s" % name)
        return data


class ViewsTest(ViewsMainTest):
    def _gnrt_rate(self, t, i=None):
        rt = models.RatesType.objects.get_or_create(name=t)[0]
        models.Rates.objects.create(date_in=_random_date(), rtype=rt)

    def _gnrt_sp(self, i=None):
        return models.StaticPage.objects.create(
            content=_stf(200), name=_stf(10))

    def test_simple_content(self):
        map(self._gnrt_sp, xrange(6))
        page = _rnd_obj('StaticPage')
        data = self._get('client-simple_content', kwargs=dict(page=page.name))
        # @TODO - add data test here

    def test_rates(self):
        map(self._gnrt_rates, xrange(20))
        for (t, name) in settings.RATES_TYPES:
            [self._gnrt_rate(t) for i in xrange(20)]
            r = _rnd_obj('Rates', dict(rtype__name=t))
            r.active = True
            r.save()


class ViewsNewsMainTest(ViewsMainTest):
    def _gnrt_note(self, i=None):
        return models.Note.objects.create(
            header=_stf(20), text=_stf(200), date=_random_date())

    def setUp(self):
        map(self._gnrt_note, xrange(50))
        self.count = int(math.ceil(
            models.Note.objects.all().count()/float(settings.NOTE_COUNT)))


class ViewsNewsTest(ViewsNewsMainTest):
    def test_news(self):
        data = self._get('client-news')
        self.assertIn('result', data)
        # @TODO - add data['result'] test here
        self.assertIn('result', data)
        self.assertIn('next_page', data)
        self.assertIn('prev_page', data)
        self.assertIn('page_count', data)

    def test_get_page(self):
        for i in xrange(2, self.count+2):
            data = self._get('client-news', query=dict(page=i))
            np = min(i+1, self.count)
            pp = max(i-1, 1)
            self.assertEqual(
                data.get('next_page'), np,
                msg="%s next %s != %s" % (i, data.get('next_page'), np))
            self.assertEqual(
                data.get('prev_page'), pp,
                msg="%s prev %s != %s" % (i, data.get('prev_page'), pp))

    def test_note(self):
        note = _rnd_obj('Note')
        data = self._get('client-newsdetail', kwargs=dict(pk=note.id))
        self.assertIn('result', data)
        # @TODO - add data['result'] test here


class ViewsIndexTest(ViewsNewsMainTest):
    def _gnrt_img(self, i=None):
        f = 'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,' + \
            '\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        img = SimpleUploadedFile('%s.gif' % _stf(), f)
        return models.Image.objects.create(
            img=img, description=_stf(),  is_displ=_rnd_bool(),
            directory='tests')

    def test_index(self):
        """
        In data:
            result - notes
            banner - banner info
        """
        map(self._gnrt_img, xrange(6))
        data = self._get('client-index')
        self.assertIn('result', data)
        # @TODO - add data['result'] test here
        self.assertIn('banner', data)
        self.assertEqual(len(data['banner']),
                         models.Image.objects.filter(is_displ=True).count())
        # @TODO - add data['banner'] items test here


class ViewsAddresesMainTest(ViewsMainTest):
    def _rnd_bld(self):
        return _rnd_obj('Building') or self._gnrt_building()

    def _gnrt_street(self, i=None):
        return models.Street.objects.create(name=_stf())

    def _gnrt_building(self, i=None):
        plan = _rnd_bool()
        return models.Building.objects.create(
            num=randint(1, 300), lat=random(), lng=random(), plan=plan,
            street=_rnd_obj('Street') or self._gnrt_street(),
            active=False if plan else _rnd_bool())


class ViewsLetsfoxTest(ViewsAddresesMainTest):
    def test_letsfox(self):
        pass


class ViewsCentrallOfficeMainTest(ViewsAddresesMainTest):
    def _gnrt_co(self, i=None):
        return models.CentralOffice.objects.create(
            name=_stf(), address=self._rnd_bld(), in_map=_rnd_bool)


class ViewsPaymentTest(ViewsCentrallOfficeMainTest):
    def _gnrt_marker(self, i=None):
        return models.MarkerIcon.objects.create(name=_stf())

    def _gnrt_payment(self, i=None, is_t=None):
        return models.Payment.objects.create(
            name=_stf(), is_terminal=_rnd_bool() if is_t is None else is_t,
            marker=_rnd_obj('MarkerIcon') or self._gnrt_marker())

    def _gnrt_pp(self, i=None):
        p = _rnd_obj('Payment', dict(is_terminal=True)) or self._gnrt_payment()
        return models.PaymentPoint.objects.create(
            name=_stf(), address=self._rnd_bld(), payment=p)

    def test_payment(self):
        pass


class ViewsAboutTest(ViewsCentrallOfficeMainTest):
    def test_about(self):
        pass

test_document!
test_vacancy!
test_how!
