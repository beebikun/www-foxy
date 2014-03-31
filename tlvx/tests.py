# -*- coding: utf-8 -*-
from datetime import datetime
import json
import math
import pytz
from random import randint, random, getrandbits
import uuid
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.test import TestCase
from django.test.client import RequestFactory
from tlvx import helpers, settings, views as tlvx_views
from tlvx.core import models
from tlvx.api import serializers


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


def _rnd_float():
    return round(random(), 10)


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
            (u'111', u'111'),
            (u'f61c04be', u'а61с04иу'),
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
    def _get_data(self, name, response):
        def _get(context):
            for c in context:
                if 'data' in c:
                    return c['data']
                if isinstance(c, (list, dict)):
                    return _get(c)
            return
        data = _get(response.context)
        self.assertTrue(
            data, msg="No data for %s : \n%s" % (name, response.context))
        return data

    def _post(self, name, data):
        response = self.client.post(reverse(name), data)
        return self._get_data(name, response)

    def _get(self, name, kwargs={}, query=None):
        query = '?' + '&'.join(
            ['%s=%s' % (k, v) for k, v in query.iteritems()]) if query else ''
        response = self.client.get(reverse(name, kwargs=kwargs) + query)
        return self._get_data(name, response)

    def _test_some_result(self, result, objects, serializer_name, fn=None):
        if fn is None:
            def fn(obj, d, i):
                return d

        obj_len = len(objects)
        r_len = len(result)
        self.assertEqual(obj_len, r_len, msg='%s - %s != %s' % (
            objects[0].__class__, obj_len, r_len))

        for i, obj in enumerate(objects):
            _s = getattr(serializers, serializer_name)(instance=obj)
            normal_data = fn(obj, _s.data, i)
            msg = "%s(%s) - %s != %s" % (obj, i, result[i], normal_data)
            self.assertEqual(normal_data, result[i], msg=msg)

    def _gnrt_sp(self, i=None, name=None):
        return models.StaticPage.objects.create(
            content=_stf(200), name=name or _stf(10))


class ViewsTest(ViewsMainTest):
    def _gnrt_rate(self, t, i=None):
        rt = models.RatesType.objects.get_or_create(name=t)[0]
        return models.Rates.objects.create(date_in=_random_date(), rtype=rt)

    def test_simple_content(self):
        map(self._gnrt_sp, xrange(6))
        page = _rnd_obj('StaticPage')
        data = self._get('client-simple_content', kwargs=dict(page=page.name))
        normal_data = serializers.StaticPageSerializer(instance=page).data
        self.assertEqual(data, normal_data)

    def test_rates(self):
        for (t, name) in settings.RATES_TYPES:
            #создаем группу тарифов
            [self._gnrt_rate(t) for i in xrange(20)]
            #случайный делаем активным
            r = _rnd_obj('Rates', dict(rtype__name=t))
            r.active = True
            r.save()
            rates = models.Rates.objects.filter(
                rtype__name=t).order_by('-date_in')
            if t == 'p':
                data = self._get('client-rates')
            else:
                data = self._get('client-ratessimple', kwargs=dict(name=t))
            self._test_some_result(data, rates, 'RatesSerializer')


class ViewsNewsMainTest(ViewsMainTest):
    def _gnrt_note(self, i=None):
        return models.Note.objects.create(
            header=_stf(20), text=_stf(200), date=_random_date())

    def _test_result(self, result, note=None):
        first = 0
        end = settings.NOTE_COUNT
        if not note:
            notes = models.Note.objects.all().order_by(
                'num', '-date')[first:end]
        else:
            notes = [note]
        self._test_some_result(result, notes, 'NoteSerializer')

    def setUp(self):
        map(self._gnrt_note, xrange(50))
        self.count = int(math.ceil(
            models.Note.objects.all().count()/float(settings.NOTE_COUNT)))


class ViewsNewsTest(ViewsNewsMainTest):
    def test_news(self):
        data = self._get('client-news')
        self.assertIn('result', data)
        self._test_result(data['result'])
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
        self._test_result(data['result'], note)


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
        images = models.Image.objects.filter(is_displ=True)
        data = self._get('client-index')
        self.assertIn('result', data)
        self._test_result(data['result'])
        self.assertIn('banner', data)
        self.assertEqual(len(data['banner']), images.count())

        def fn(obj, d, i):
            d['num'] = i
            d['url'] = obj.get_img_absolute_urls()
            return d

        self._test_some_result(data['banner'], images, 'ImageSerializer', fn)


class ViewsAddresesMainTest(ViewsMainTest):
    def _rnd_bld(self):
        return _rnd_obj('Building') or self._gnrt_building()

    def _gnrt_street(self, i=None):
        return models.Street.objects.create(name=_stf())

    def _gnrt_building(self, i=None):
        plan = _rnd_bool()
        return models.Building.objects.create(
            num=randint(1, 300), lat=_rnd_float(), lng=_rnd_float(), plan=plan,
            street=_rnd_obj('Street') or self._gnrt_street(),
            active=False if plan else _rnd_bool())


class ViewsCentrallOfficeMainTest(ViewsAddresesMainTest):
    def _gnrt_co(self, i=None, in_map=None):
        return models.CentralOffice.objects.create(
            name=_stf(), address=self._rnd_bld(),
            in_map=_rnd_bool if in_map is None else in_map)


class ViewsLetsfoxTest(ViewsCentrallOfficeMainTest):
    def setUp(self):
        [self._gnrt_building, xrange(30)]
        [self._gnrt_co(in_map=True) for i in xrange(5)]
        for b in models.Building.objects.iterator():
            b.co = _rnd_obj('CentralOffice')
            b.save()

    def test_letsfox(self):
        # @TODO: add test for other situations:
        # - exact matching [done]
        # - exact matching and simmular
        # - only simmular
        # - no result
        bld = self._rnd_bld()
        data = self._post('client-letsfox',
                          dict(street=bld.street.name, num=bld.num))
        self.assertIn('params', data)
        street = tlvx_views.change_keyboard(bld.street.name)
        num = str(bld.num)
        self.assertEqual(street, data['params'].get('street'))
        self.assertEqual(num, data['params'].get('num'))
        result = data.get('result')
        self.assertTrue(result)
        bld_data = serializers.BuildingSerializer(instance=bld).data
        bld_data['result'] = True
        bld_data[u'co'] = bld.co and '%s, %s' % (
            bld.co.contacts or '', bld.co.schedule or '')
        self.assertIn(bld_data, result)


class ViewsPaymentTest(ViewsCentrallOfficeMainTest):
    page = lambda self, n: serializers.StaticPageSerializer(
        instance=models.StaticPage.objects.get(name=n)).data

    def _gnrt_marker(self, i=None):
        return models.MarkerIcon.objects.create(name=_stf())

    def _gnrt_payment(self, i=None, is_t=None, name=None):
        return models.Payment.objects.create(
            name=name or _stf(),
            is_terminal=_rnd_bool() if is_t is None else is_t,
            marker=_rnd_obj('MarkerIcon') or self._gnrt_marker())

    def _gnrt_pp(self, i=None, p=None):
        p = p or _rnd_obj(
            'Payment', dict(is_terminal=True)) or self._gnrt_payment()
        return models.PaymentPoint.objects.create(
            name=_stf(), address=self._rnd_bld(), payment=p)

    def setUp(self):
        map(self._gnrt_payment, xrange(3))

    def test_payment(self):
        pass

    def test_paymentcard(self):
        payments = models.Payment.objects.filter(
            is_terminal=False).order_by('num')
        data = self._get('client-paymentcard')
        self._test_some_result(data, payments, 'PaymentSerializer')

    def test_paymentelmoney(self):
        instruction = self._gnrt_sp(name='asist-instruction')
        returns = self._gnrt_sp(name='asist-returns')
        inn = self._gnrt_sp(name='payment-elmoney-inn')
        data = self._get('client-paymentelmoney')
        self.assertIn('instruction', data)
        self.assertIn('returns', data)
        self.assertIn('inn', data)
        self.assertEqual(self.page(instruction), data['instruction'])
        self.assertEqual(self.page(returns), data['returns'])
        self.assertEqual(self.page(inn), data['inn'])

    def test_paymentlimit(self):
        limit = self._gnrt_sp(name='payment-limit')
        data = self._get('client-paymentlimit')
        self.assertEqual(self.page(limit), data)

    def test_paymentmobile(self):
        data = self._get('client-paymentmobile')
        self.assertIn('gray_ip', data)
        self.assertTrue(isinstance(data['gray_ip'], bool))

    def test_paymentterminal(self):
        def _clear(s):
            if not s:
                return
            s = s.replace('&', '&amp;')
            while s.find('"') >= 0:
                i = s.find('"')
                s = s[:i] + '&laquo;' + s[i+1:]
                i = s.find('"')
                s = s[:i] + '&raquo;' + s[i+1:]
            return s

        def _equal(data, obj, values):
            name = values.pop()
            self.assertEqual(_clear(getattr(obj, name)),
                             data.get(name))
            return _equal(data, obj, values) if values else None

        def fn(obj, data, i):
            def _unclear(s, values=None):
                if not s:
                    return
                if values is None:
                    values = [('&amp;', '&'), ('&laquo;', '"'),
                              ('&raquo;', '"')]
                v = values.pop()
                s = s.replace(v[0], v[1])
                return _unclear(s, values) if values else s

            data['name'] = _unclear(data['name'])
            data['address'] = _unclear(data['address'])
            if isinstance(obj, models.CentralOffice):
                data['id'] = models.PaymentPoint.objects.aggregate(
                    Max('id')).get('id__max') + data['id']
            return data

        map(self._gnrt_co, xrange(5))
        co = self._gnrt_payment(name=u'Офисы продаж')
        map(self._gnrt_pp, xrange(30))
        payments = models.Payment.objects.filter(is_terminal=True)
        data = self._get('client-paymentterminal')
        self.assertEqual(payments.count(), len(data))
        for p in data:
            self.assertTrue(isinstance(p.get('id'), int))
            payment = models.Payment.objects.get(id=p.get('id'))
            _equal(p, payment, ['name', 'description'])
            self.assertIn('points', p)
            self.assertIn('result', p['points'])
            if payment != co:
                points = payment.get_points()
            else:
                points = models.CentralOffice.objects.filter(in_map=True)
            self.assertEqual(len(points), len(p['points']['result']))
            self._test_some_result(p['points']['result'], points,
                                   'PaymentPointSerializer', fn)


class ViewsAboutTest(ViewsCentrallOfficeMainTest):
    def test_about(self):
        co = [self._gnrt_co(in_map=True) for i in xrange(5)]
        [self._gnrt_co(in_map=False) for i in xrange(5)]
        data = self._get('client-about')
        result = data.get('result')
        self.assertTrue(result)
        self.assertEqual(len(co), len(result))

        def fn(obj, data, i):
            data['ico'] = obj.marker and obj.marker.name
            return data

        self._test_some_result(result, co, 'PaymentPointSerializer', fn)


class ViewsTreePageMainTest(ViewsMainTest):
    def _gnrt_page(self, i=None, parent=None):
        params = dict(name=_stf(), display_name=_stf(), content=_stf())
        if parent:
            params['parent'] = parent
        page = self.model.objects.create(**params)
        if _rnd_bool():
            self._gnrt_page(parent=page)
        return page

    def setUp(self):
        map(self._gnrt_page, xrange(10))


class ViewsDocumentTest(ViewsTreePageMainTest):
    model = models.DocumentsPage

    def test(self):
        pass


class ViewsHowTest(ViewsTreePageMainTest):
    model = models.HelpPage

    def test(self):
        pass


class ViewsVacancyTest(ViewsTreePageMainTest):
    model = models.VacancyPage

    def _gnrt_page(self, parent=None):
        root = self.model.objects.get_or_create(name='vacancy')[0]
        return self.model.objects.create(
            parent=root, name=_stf(), display_name=_stf())

    def test(self):
        pass



# test_clientrequest
# test captcha
