# -*- coding: utf-8 -*-
import json
import time
import urllib2
from django.core.exceptions import FieldError
from tlvx.settings import GIS_CONFIG


def get_gis_url(suf=''):
    return '%s%s?key=%s&version=%s&' % (
        GIS_CONFIG['url'], GIS_CONFIG[suf],
        GIS_CONFIG['key'], GIS_CONFIG['version'])


def make_get(url):
    #спим 1 секунду, чтобы 2гис не считал что мы его ддосим
    time.sleep(0.1)
    req = urllib2.Request(url.encode('utf-8'))
    req.add_header('Content-Type', 'application/json')
    # Делаем запрос в 2гис
    response = json.loads(urllib2.urlopen(req).read())
    if response.get('response_code') != u'200':
        raise FieldError(u'Bad 2gis answer %s (%s) for url:\n%s' % (
            response.get('response_code'), response.get('error_message'), url))
    return response


def get_gis_answer(url, city, street, num, street_alt, num_alt):
    def clear(n):
        if isinstance(n, basestring):
            n = n.encode('utf-8', 'ignore').decode('ascii', 'ignore')
        else:
            n = str(n)
        return n.lower().replace(' ', '').replace(u'стр', '')
    response = make_get(url)
    if response.get('total') != u'1':
        raise FieldError('Response is too long')
    #Если объектов в ответе один
    result = response.get('result', {})[0]
    if result.get("type") != 'house':
        raise FieldError('Bad geoobject type: %s' % result.get("type"))
    # Проверяем, что в ответе город, улица и дом
    # совпадают с городом, улицей и домом в self
    attr = result.get('attributes', {})
    clear_num = clear(num)
    clear_num_alt = clear(num_alt)
    result_num = clear(attr.get('number', ''))
    result_num_alt = clear(attr.get('number2', ''))
    num_match = \
        result_num == clear_num \
        or num_alt and result_num == clear_num_alt \
        or num_alt and result_num_alt == clear_num_alt \
        or result_num_alt == clear_num \
        or False
    street_match = \
        attr.get('street') == street \
        or street_alt and attr.get('street') == street_alt \
        or attr.get('street2') == street \
        or street_alt and attr.get('street2') == street_alt \
        or False
    if attr.get('street') == u'Рёлочный пер' \
            and (street == u'пер. Рёлочный' or street_alt == u'пер. Рёлочный'):
        street_match = True   # ^ - X_X
    if attr.get('city') == city and street_match and num_match:
        return result
    else:
        # Если не совпадает - так и пишем
        raise FieldError(u'Params not match! \
            Params in response: (%s, %s, %s); \
            params in query: (%s, %s, %s) \
            alt params in response: (%s, %s)\
            alt params in query: (%s, %s)' % (
            attr.get('city'), attr.get('street'), result_num,
            city, street, num,
            attr.get('street2'), result_num_alt,
            street_alt, num_alt))
