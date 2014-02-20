# -*- coding: utf-8 -*-
ENTER_TITLE = {
    'ok':u'BGBilling || Новости',
    'bad':u'Ошибка при авторизации | Televox'
}
import httplib, urllib
import re
import cookielib, urllib2
import lxml.html
def post(data='', url="www.tele-vox.ru", cj=None):
    if not cj:
        cj = cookielib.CookieJar()        
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [
        ('User-Agent', 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.11) Gecko/20101012 Firefox/3.6.11'),        
        ('Content-type', "application/x-www-form-urlencoded"),
        ("Accept", "text/plain")
    ]
    if data:
        params = urllib.urlencode(data)
        home = opener.open('http://%s'%url, params)        
    else:
        home = opener.open('http://%s'%url)
    return home.read().decode('utf-8'), cj

def clearing_value(s, clear_list=None):
    if clear_list==None:
        clear_list = ['\t','<title>','</title>','  ','\n']
    if len(clear_list):
        clear = clear_list.pop()
        return clearing_value(s.replace(clear,''),clear_list)
    else:
        return s

def find_title(data):
    c = re.compile(r'<title>[\s\S]+</title>')
    search = re.search(c, data)
    return search and clearing_value(search.group())

def find_limit(data):
    search = re.search(u'Текущий лимит: [-?\d\.?]+', data)
    return search and search.group()

def take_limit(user, pswd):
    url = "www.tele-vox.ru"
    data, cj = post({'user': user, 'pswd': pswd}, url)
    title = find_title(data)
    if title == ENTER_TITLE['ok']:
        search_contract_id = re.search(u'contractId=[\w]+', data)
        contract_id = search_contract_id and search_contract_id.group().replace('contractId=','')
        limit_url = \
            "%s/?action=ContractLimit&mid=0&module=contract&contractId=%s"%(
                url, contract_id)
        limit_value_data, cj = post({}, limit_url, cj) 
        limit_value = find_limit(limit_value_data)
        page = lxml.html.fromstring(limit_value_data)
        #limit_hint = page.cssselect('.comment')[0].text
        limit_hint = u'Восстановление лимита происходит при внесении на лицевой счет платежа, равного размеру лимита или превышающего его. При этом статус обещанного платежа меняется на "Погашен".'
        if not limit_value or not int(re.search('[\d]+',limit_value).group()):                        
            data_limit, cj = post({'summ':'200','days':'2'}, limit_url, cj)
            limit = find_limit(data_limit)
            message = u'%s<br>%s'%(limit,limit_hint)
        else:
            message = u'Лимит на вашем лицевом счете уже взят.<br>%s<br>%s'%(
            	limit_value, limit_hint)
    elif title == ENTER_TITLE['bad']:
        message = u'Ошибка авторизации'
    else:
        message == u'Неизвестная ошибка: %s'%title
    return message
