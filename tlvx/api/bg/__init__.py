# -*- coding: utf-8 -*-
import cookielib
import re
import urllib2
from .errors import BgException, LoginException


class BGBilling(object):
    """Класс для связи с личным кабинетом BGBilling"""
    MAIN_URL = "www.tele-vox.ru"
    LOGIN_TITLE = {
        'ok': u'BGBilling || Новости',
        'bad': u'Ошибка при авторизации | Televox'
    }
    LIMIT_HINT = u'Восстановление лимита происходит при внесении на ' + \
        u'лицевой счет платежа, равного размеру лимита или превышающего' + \
        u' его. При этом статус обещанного платежа меняется на "Погашен".'
    LIMIT_URL = lambda self: "action=ContractLimit&mid=0" + \
        "&module=contract&contractId=" + self.contract_id
    LIMIT_WRN = u'Лимит на вашем лицевом счете уже взят.<br>'

    def __init__(self, lgn, pswd):
        self.cj = cookielib.CookieJar()
        start_page = self._post(data=dict(user=lgn, pswd=pswd))
        title = self._find_in(start_page, r'<title>[\s\S]+</title>',
                              ['\t', '<title>', '</title>', '  ', '\n'])
        if title == self.LOGIN_TITLE['bad']:
            raise LoginException(reason=u'Ошибка авторизации')
        if title != self.LOGIN_TITLE['ok']:
            raise LoginException(reason=u'Неизвестная ошибка: %s' % title)
        self.contract_id = self._find_in(
            start_page, ur'contractId=[\w]+', ['contractId='])

    def _find_in(self, data, pattern, replace=[]):
        search = re.search(pattern, data)
        val = search.group() if search else ''
        clear = lambda v, r: clear(v.replace(r.pop(), ''), r) if r else v
        return clear(val, replace)

    def _post(self, url=None, data={}, query=''):
        if url is None:
            url = self.MAIN_URL
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6;' +
                ' en-US; rv:1.9.2.11) Gecko/20101012 Firefox/3.6.11'),
            ('Content-type', "application/x-www-form-urlencoded"),
            ("Accept", "text/plain")
        ]
        q = '&'.join(['%s=%s' % (k, v) for k, v in data.iteritems()]) + \
            '&' + query
        page = opener.open('http://%s?%s' % (url, q.encode('utf-8')))
        return page.read().decode('utf-8')

    def take_limit(self):
        def _get_limit_string(data={}):
            page = self._post(data=data, query=self.LIMIT_URL())
            return self._find_in(page, ur'Текущий лимит: [-?\d\.?]+')

        limit_string = _get_limit_string()
        limit_value = re.search('[\d]+', limit_string).group()
        msg = ''
        if not limit_string or not (limit_value and int(limit_value)):
            limit_string = _get_limit_string(dict(summ=200, days=2))
        else:
            msg = self.LIMIT_WRN
        return "%s%s<br>%s" % (msg, limit_string, self.LIMIT_HINT)


def take_limit(user, pswd):
    try:
        bg = BGBilling(user.strip(), pswd.strip())
        return bg.take_limit()
    except BgException, e:
        return e.reason
