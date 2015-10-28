# -*- coding: utf-8 -*-
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.MIMEBase import MIMEBase
from email import Encoders
import os
import smtplib
import math
from django.utils import timezone
from django.shortcuts import get_object_or_404
from tlvx import settings

_eng_chars = u'~!@#$%^&qwertyuiop[]asdfghjkl;\'zxcvbnm,.QWERTYUIOP{}ASDFGHJKL:\"|ZXCVBNM<>?'
_rus_chars = u'ё!\"№;%:?йцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ,'
_both_chars = u'.,'
_trans_table = dict(zip(_eng_chars, _rus_chars))


def change_keyboard(s):
    def _check(i, c):
        is_tmp = (i, c) if (c in _both_chars) else None
        new_c = _trans_table.get(c)
        return new_c or c, is_tmp, new_c and not is_tmp
    s, tmp, is_ch = zip(*[_check(i, c) for i, c in enumerate(s)])
    tmp = filter(lambda v: isinstance(v, tuple), tmp)
    is_ch = filter(lambda c: c, is_ch)
    s = list(s)
    if tmp and not is_ch:
        for i, c in tmp:
            s[i] = c
    return u''.join(s)


def sendEmail(subject='', html='', to=None, attach=None):
    mail = MIMEMultipart('alternative')
    mail['From'] = settings.CONN_SPAM['from']
    pswd = settings.CONN_SPAM['pswd']
    srv = (settings.CONN_SPAM['server'], settings.CONN_SPAM['port'])
    mail['To'] = to or settings.CONN_SPAM['to']
    mail['Subject'] = Header(subject, 'utf-8')
    body = MIMEText(html.encode('utf-8'), 'html')
    mail.attach(body)
    if attach:
        f = MIMEBase('application', "octet-stream")
        f.set_payload(open(attach, "rb").read())
        Encoders.encode_base64(f)
        f.add_header(
            'Content-Disposition', 'attachment; filename="%s"' %
            os.path.basename(attach))
        mail.attach(f)
    server = smtplib.SMTP("%s:%s" % srv)
    server.starttls()
    server.login(mail['From'], pswd)
    server.sendmail(
        mail['From'], mail['To'], mail.as_string())
    server.quit()


def paginator(count, cur):
    """Утилита для паджинатора(страница новости).
    Паджинатор представляет собой уи, в котором можно перейти на
    страницу вперед, на страницу назад, в нем отображается текущая страница,
    а также некоторое количество(settings.PAGINATOR_PAGE) страниц, соседних
    с текущей. Остальные страницы заменены на (..).
    Т.е, паджинатор имеет вид
    <-(1)(...)(10)(11)(12)(...)(LAST)->
    Так вот, данная функция считает и возвращает список номеров страниц,
    которые будут отображаться вместо (10)(11)(12).
    Args:
        - count - int, количество страниц всего
        - cur - int, номер текущей страницы
    Returns:
        Список из int
    """
    #Проверяем, что settings.PAGINATOR_PAGE - нечетное. иначе - отнимаем 1
    paginator_page = settings.PAGINATOR_PAGE if (
        settings.PAGINATOR_PAGE % 2) else settings.PAGINATOR_PAGE - 1
    #Определяем действительное количество отображаемых страниц
    #Для этого отнимает 4 страницы(вперед, назад, (...), (...))
    displayP = paginator_page - 4
    empty = ['...']
    #Определяем, какое количество страниц будет отображаться справа
    #и слева от текущей
    half = (displayP-1)/2
    left = cur - half  # левый край
    right = cur + half + 1  # правый край
    left_end = count - displayP + 1  # от конца и назад
    right_start = displayP + 1  # от начала и вперед
    if left_end <= 2 and right_start >= count:
        pages = range(2, count)
    elif left <= 2:  # для случаев <-(1)(2)(3)(...)(LAST)->
        pages = range(2, right_start) + empty
    elif right >= count:  # для случаев <-(1)(...)(51)(52)(53)->
        pages = empty + range(left_end, count)
    else:  # для случаев <-(1)(...)(10)(11)(12)(...)(53)->
        pages = empty + range(left, right) + empty
    if count > 1:
        pages.append(count)
    return [1] + pages


def get_news(srlz, model, page=1, pk=None, count=None):
    data = dict()
    if not pk:
        #Возвращаем требуемое settings.NOTE_COUNT
        #новостей на требуемой странице
        params = dict(
            count=count or settings.NOTE_COUNT,
            page=page if isinstance(page, int) else 1)
        first = params['count']*(params['page']-1)
        end = params['count']*params['page']
        notes = model.objects.filter(
            date__lte=timezone.now()).order_by('num', '-date')
        objects = notes[first:end]
        data.update(
            page=params['page'],
            page_count=int(math.ceil(notes.count()/float(params['count'])))
        )
        #Следующие 3 поля - для пэйджинатора, чтобы не делать этого в клиенте
        data['display_page'] = paginator(data['page_count'], data['page'])
        data['prev_page'] = max(1, data['page']-1)
        data['next_page'] = min(data['page']+1, data['page_count'])
    else:
        #Возвращаем требуемую нововсть
        objects = [get_object_or_404(model, pk=pk)]
    data['result'] = map(
        lambda obj: srlz(instance=obj).data,
        objects)
    return data
