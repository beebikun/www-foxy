# -*- coding: utf-8 -*-
import re
import requests
from .errors import BgException, LoginException
from django.conf import settings


class BGBilling(object):
    """Класс для связи с личным кабинетом BGBilling"""
    BASE_URL = "http://www.tele-vox.ru"
    LIMIT_WRN = u'Лимит на вашем лицевом счете уже взят.'
    LIMIT_SCS = u'Лимит для вашего лицевого счета понижен.'

    def login(self, lgn, pswd):
        self.s = requests.session()
        data = {'user': lgn, 'pswd': pswd}
        r = self.s.post(self.BASE_URL, data=data)
        title_re = re.search(ur'class="pageTitle">([\S\s]+?)</div>', r.text)
        title = title_re.groups()[0].strip() if title_re else u''
        if title != u'Договор № {}'.format(lgn):
            raise LoginException(reason=title)
        return r.text

    def __init__(self, lgn=None, pswd=None):
        if settings.DEBUG and lgn is None:
            lgn = '000001'
            pswd = '111111'
        self.html = self.login(lgn, pswd)

    def take_limit(self):
        def check_limit(html):
            return re.search(ur'Текущий лимит: (\-?\d+)', html).groups()[0]

        prefix = re.search(ur'<a href="(\?action=ContractLimit&mid=0&module=contract&contractId=\d+)">', self.html)
        if prefix is None:
            raise BgException(u'Неизвестная ошибка')

        prefix = prefix.groups()[0]
        url = '{}/webexecuter{}'.format(self.BASE_URL, prefix)

        limit_page = self.s.get(url).text
        if check_limit(limit_page) != '0':
            return self.LIMIT_WRN

        result = self.s.post(url, data={'act': u'Подключить'}).text
        if check_limit(result) == '0':
            raise BgException(u'Неизвестная ошибка')

        return self.LIMIT_SCS


def take_limit(user=None, pswd=None):
    if settings.DEBUG and user is None:
        user = '000001'
        pswd = '111111'
    try:
        bg = BGBilling(user.strip(), pswd.strip())
        return bg.take_limit()
    except BgException, e:
        return e.reason
