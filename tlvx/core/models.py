# -*- coding: utf-8 -*-
import json
import os
from django.db.models import Q
import re
import uuid
from django.core.exceptions import FieldError
from django.db import models
from django.utils import dateformat
from django.utils import timezone
from imagekit import models as imagekit_models
from imagekit import processors
from tlvx.settings import BUILD_TYPES, NOTE_TYPES, RATES_TYPES, \
    DATE_FORMAT, DEFAULT_IMAGE_HOST_URL, CONN_SPAM
from tlvx.helpers import sendEmail
from tlvx.core.gis import get_gis_url, make_get, get_gis_answer


formatted_date = lambda date: dateformat.format(date, DATE_FORMAT)


class City(models.Model):
    name = models.CharField(max_length=256, unique=True)

    get_builds_sum = lambda self: len(self.buildings.all())

    def __unicode__(self):
        return self.name


class Street(models.Model):
    name = models.CharField(max_length=256, unique=True)

    get_builds_sum = lambda self: len(self.buildings.all())

    def __unicode__(self):
        return self.name


class CentralOffice(models.Model):
    name = models.CharField(max_length=256, unique=True)
    address = models.ForeignKey('Building', blank=True, null=True)
    in_map = models.BooleanField(
        blank=True, default=True,
        verbose_name=u"Отображать на карте в контактах или нет")
    contacts = models.CharField(max_length=256, null=True)
    schedule = models.CharField(
        max_length=1024, null=True,
        default=u"Ежедневно, с 9:00 до 21:00", verbose_name="График работы")
    marker = models.ForeignKey(
        "MarkerIcon", blank=True, null=True,
        verbose_name=u"Иконка маркера на карте",
        related_name="offices")

    lat = lambda self: self.address.lat

    lng = lambda self: self.address.lng

    get_address = lambda self: self.address.get_address()

    get_builds_sum = lambda self: len(self.buildings.all())

    def __unicode__(self):
        return str(self.pk)


class BuildType(models.Model):
    """
    Жилое или офисное
    """
    name = models.CharField(max_length=256, choices=BUILD_TYPES, unique=True)

    get_builds_sum = lambda self: len(self.buildings.all())

    def __unicode__(self):
        return self.name


class Square(models.Model):
    """
    Номер квартала.
    """
    num = models.IntegerField(unique=True)

    get_builds_sum = lambda self: len(self.buildings.all())

    def __unicode__(self):
        return str(self.num)


class NoteType(models.Model):
    """
    Тип заметки - новости, авария
    """
    name = models.CharField(max_length=256, choices=NOTE_TYPES, unique=True)

    get_notes_sum = lambda self: len(self.notes.all())

    def __unicode__(self):
        return self.name


class BuildingManager(models.Manager):
    def filter_simmular(self, street, num, result=None):
        """Из списка всех зданий, за исключением того,
        которое уже выдстся как результат, находит те, который в адресе или
        альтернативном адресе содержат нужные паттерны названия улицы
        и номера дома"""
        fltr = self.exclude(id=result.id if result else 0).filter
        return fltr(num__icontains=num, street__name__icontains=street) | \
            fltr(num_alt__icontains=num, street_alt__name__icontains=street)

    def get_is_active_iterator(self):
        return Building.objects.filter(active=True).iterator()

    def get_in_plan_iterator(self):
        return Building.objects.filter(plan=True).iterator()


class Building(models.Model):
    objects = BuildingManager()
    num = models.CharField(max_length=256)
    street = models.ForeignKey("Street", related_name="buildings")
    #Для домов с двойным адресом
    num_alt = models.CharField(max_length=256, blank=True, null=True,)
    street_alt = models.ForeignKey(
        "Street", related_name="buildings_alt", blank=True, null=True,)
    city = models.ForeignKey("City", related_name="buildings", blank=True, null=True)
    square = models.ForeignKey(
        "Square", blank=True, null=True, related_name="buildings")
    co = models.ForeignKey(
        "CentralOffice", blank=True, null=True, related_name="buildings")
    # btype = models.ForeignKey("BuildType", blank=True, null=True,
    #     related_name="buildings")

    date = models.DateTimeField(
        auto_now_add=True, verbose_name=u"дата заведения")
    active = models.BooleanField(
        default=False, verbose_name=u"введен в эксплуатацию или нет")
    plan = models.BooleanField(
        default=False, verbose_name=u"В планах или нет")
    date_in = models.DateTimeField(
        default=None, blank=True, null=True,
        verbose_name=u"дата ввода в эксплуатацию")

    #Поля с 2 гис
    lat = models.FloatField(
        blank=True, null=True,
        verbose_name="latitude of position for place")
    lng = models.FloatField(
        blank=True, null=True,
        verbose_name="longitude of position for place")
    name = models.CharField(max_length=256, blank=True, null=True, )

    get_pp = lambda self: len(self.points.all())

    get_position = lambda self: [self.lat, self.lng]

    def search_by_address(self, street='', num=''):
        if street.lower() in self.street.name.lower() and \
                num.lower() in self.num.lower():
            return True
        if self.street_alt and \
            street.lower() in self.street_alt.name.lower() and \
                num.lower() in self.num_alt.lower():
            return True
        return False

    def save(self, *args, **kwargs):
        if not self.pk:
            """
            Если кваргс - значит создается новая запись в бд,
            в моем случае - это значит, что идет создание объекта
            Проверяем, что в бд нет адреса с такими параметрами (улица. дом)
            и, если нет, устанавливаем координаты места.
            Также, если не передан город - устанавливаем благовещенск.
            Если не передан тип строения - устанавливаем "жилое".
            Если здание active - устанавливаем date_in
            """
            # Проверяем что не существует дома с таким адресом
            filter_by_street_num = Building.objects.filter(
                num=self.num, street=self.street)
            #Проверяем, что нет дома, у которого альт адрес - адрес нового
            filter_by_street_num_nrm_as_alt = Building.objects.filter(
                num_alt=self.num, street_alt=self.street)
            filter_list = list(filter_by_street_num) + \
                list(filter_by_street_num_nrm_as_alt)
            if self.num_alt and self.__dict__.get('street_alt_id'):
                #Проверяем, что не существует дома с таким
                #алтернативным адресом
                filter_by_street_num_alt = Building.objects.filter(
                    num_alt=self.num_alt, street_alt=self.street_alt)
                #Проверяем, что нет дома у которого норм адрес -
                #альт адрес нового дома
                filter_by_street_num_alt_as_nrm = Building.objects.filter(
                    num=self.num_alt, street=self.street_alt)
                filter_list = filter_list + list(filter_by_street_num_alt) + \
                    list(filter_by_street_num_alt_as_nrm)
            if filter_list and not self.pk:
                raise FieldError("Building arleady exist: %s" % filter_list)
            if self.active and self.plan:
                raise FieldError("Building can't be active and in plan! \
                    Choose something one, %s" % self.get_address())
            if not self.__dict__.get('city_id'):
                city = City.objects.get_or_create(
                    name=u"Благовещенск")
                self.city = city[0]
            if not self.__dict__.get('btype_id'):
                btype = BuildType.objects.get_or_create(
                    name="house")
                self.btype = btype[0]
            if self.active:
                self.date_in = timezone.now()
            if (not self.num_alt and self.__dict__.get('street_alt_id')) or (
                    self.num_alt and not self.__dict__.get('street_alt_id')):
                raise FieldError(u"Alt params is not full: %s" % self.__dict__)
            if not self.lat and not self.lng:
                try:
                    self.get_position_from_gis()
                except FieldError, e:
                    raise FieldError(
                        u"Position for building %s was not recieved : %s" % (
                            self.get_address(), e.args[0]))
                try:
                    self.get_info_from_gis()
                except FieldError, e:
                    raise FieldError(
                        u"Info for building %s was not recieved : %s" % (
                            self.get_address(), e.args[0]))
        else:
            """
            Если место апдейтится, а не создается - проверяем,
            изменилось ли поле active.
            Если раньше оно было false, а стало True -
            меняем plan на false и устанавливаем date_in
            """
            #if not self.pk:
            #    raise FieldError("Building was not exist", self.get_address())
            old = Building.objects.get(pk=self.pk)
            if not old.active and self.active:
                self.plan = False
                self.date_in = timezone.now()
        super(Building, self).save(*args, **kwargs)

    def get_address(self):
        if self.street and self.num:
            return '%s, %s' % (self.street.name, self.num)
        return ''

    def get_address_alt(self):
        if self.street_alt and self.num_alt:
            return self.street_alt.name + ', ' + self.num_alt
        return ''

    get_params_for_gis = lambda self, url: dict(
        url=url, city=self.city.name, street=self.street.name, num=self.num,
        street_alt=self.street_alt and self.street_alt.name,
        num_alt=self.num_alt)

    def get_info_from_gis(self):
        #вытягиваем название места
        url = get_gis_url('get') + 'id=' + self.gis_id
        result = get_gis_answer(**self.get_params_for_gis(url))
        if result:
            self.name = result.get('buildingname') or result.get('purpose')

    def get_position_from_gis(self):
        url = get_gis_url('search') + 'q=%s %s %s' % (
            self.city.name, self.street.name, self.num)
        result = get_gis_answer(**self.get_params_for_gis(url))
        if result:
            #берем значение поинт
            point = result.get('centroid')
            if not point:
                raise FieldError("No point in 2gis response")
            # вытаскивает лат и лнг из точки
            try:
                position = [float(f) for f in re.findall('[\d\.]+', point)]
            except ValueError, e:
                if 'could not convert string to float' in e.args[0]:
                    raise FieldError(u"Bad values in point: %s" % point)
                raise e
            if not position or len(position) != 2:
                raise FieldError(u"Bad values in point: %s" % point)
            self.lng, self.lat = position
            self.gis_id = result.get('id')
            if not self.gis_id:
                raise FieldError('Null falue for gis_id')
            attr = result.get('attributes', {})
            if attr.get('street2') and not self.street_alt:
                street_alt = attr.get('street2')
                street = attr.get('street')

                def compare_street(name_gis, name, alt_name_gis):
                    straight = name_gis == name
                    wtf = name_gis == u'Рёлочный пер' and \
                        name == u'пер. Рёлочный'
                    return (straight or wtf) and Street.objects.filter(
                        name=alt_name_gis)
                if compare_street(street, self.street.name, street_alt):
                    self.street_alt = Street.objects.get(name=street_alt)
                    self.num_alt = attr.get('number2', '')
                if compare_street(street_alt, self.street.name, street):
                    self.street_alt = Street.objects.get(name=street)
                    self.num_alt = attr.get('number', '')
            return True

    def __unicode__(self):
        return self.get_address()


class Note(models.Model):
    header = models.CharField(max_length=256, default='')
    text = models.TextField()
    date = models.DateTimeField(
        default=timezone.now, verbose_name=u"дата написания")

    ntype = models.ForeignKey(
        "NoteType", blank=True, null=True,
        verbose_name=u"тип заметки", related_name="notes")

    addresses = models.ManyToManyField(
        Building, null=True, blank=True, verbose_name=u"Адреса")
    attach = models.FileField(upload_to="notes",  null=True, blank=True)
    num = models.IntegerField(null=True, blank=True)

    attach_path = lambda self: ''

    normal_date = lambda self: formatted_date(self.date)

    def __unicode__(self):
        return "%s: %s" % (self.id, self.header)


class RatesType(models.Model):
    """Юр лица, физ лица, прочее """
    name = models.CharField(max_length=256, choices=RATES_TYPES, unique=True)

    def __unicode__(self):
        return self.name


class Rates(models.Model):
    """docstring for RatesType"""
    tables = models.TextField(
        verbose_name=u"Здесь табличка с тарифами",
        default='''\
        <table>
            <tbody>
                <tr>
                    <td></td>
                    <td></td>
                </tr>
                <tr>
                    <td></td>
                    <td></td>
                </tr>
            </tbody>
        </table>
        <span class="help-block">footnote here</span>
        <p>text here</p>
        ''')
    active = models.BooleanField(
        default=False,
        # verbose_name=u"Активен тариф или нет.
        #     Активные на главной - остальное в архив"
    )
    date_in = models.DateTimeField(
        blank=True, null=True,
        # verbose_name=u"дата, с которой действуют тарифы"
    )
    name = models.CharField(max_length=256, blank=True, null=True,
                            verbose_name=u"Название для линейки тарифов")
    date = models.DateTimeField(
        default=timezone.now, verbose_name=u"дата создания")
    date_out = models.DateTimeField(
        blank=True, null=True,
        verbose_name=u"дата, до которой действуют тарифы")
    rtype = models.ForeignKey(
        "RatesType", blank=True, null=True,
        # verbose_name=u"для физических или для юридических лиц"
    )

    normal_date = lambda self: formatted_date(self.date_in)

    def save(self, *args, **kwargs):
        if kwargs:
            if not self.__dict__.get('rtype_id'):
                rtype = RatesType.objects.get_or_create(name='p')[0]
                self.rtype = rtype
            if self.active:
                self.date_in = timezone.now()
        if self.pk:
            old = Rates.objects.get(pk=self.pk)
            if old.active and not self.active:
                self.date_out = timezone.now()
        if self.active:
            if not self.date_in:
                self.date_in = timezone.now()
            pre_active = Rates.objects.filter(
                rtype_id=self.__dict__.get('rtype_id'), active=True).exclude(
                id=self.id or 0)
            if pre_active.count():
                pre_active.update(active=False)
        if self.date_out and self.active:
            self.date_out = timezone.now()
        super(Rates, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s-%s (%s)' % (self.date_in, self.name, self.active)


class PaymentPoint(models.Model):
    address = models.ForeignKey("Building", related_name="points")
    payment = models.ForeignKey("Payment", related_name="points")
    name = models.CharField(max_length=256,)
    schedule = models.CharField(max_length=2048, blank=True, default=u'')
    gis_id = models.CharField(max_length=256, blank=True, default=u'')
    gis_hash = models.CharField(max_length=256, blank=True, default=u'')
    contacts = models.CharField(max_length=2048, blank=True, default=u'')

    lat = lambda self: self.address.lat

    lng = lambda self: self.address.lng

    get_address = lambda self: self.address.get_address()

    def save(self, *args, **kwargs):
        if kwargs:
            old = PaymentPoint.objects.filter(
                address__id=self.__dict__.get('address_id'),
                payment__id=self.__dict__.get('payment_id'),
                name=self.name)
            if old:
                raise FieldError(u'PaymentPoint arleady exist: %s' % old)
            self.get_info_from_gis()
            self.schedule = self.schedule or u'{}'
            self.contacts = self.contacts or u'{}'
            self.gis_id = self.gis_id or u''
            self.gis_hash = self.gis_hash or u''
        super(PaymentPoint, self).save(*args, **kwargs)

    def get_info_from_gis(self):
        if not (self.gis_id and self.gis_hash):
            search_prfx = u'what=%s&point=%s,%s' % (
                self.name, self.lng(), self.lat())
            url_search = get_gis_url('search_point') + search_prfx
            try:
                response_search = make_get(url_search)
            except FieldError, e:
                return
            if response_search.get('total') < 1:
                raise FieldError('response_search is empty')
            result_search = response_search.get('result')[0]
            self.gis_id = result_search.get('id')
            self.gis_hash = result_search.get('hash')
        if not self.gis_hash or not self.gis_id:
            raise FieldError('Bad value in result_search: %s %s' % (
                self.gis_id, self.gis_hash))
        url_profile = get_gis_url('profile') + 'id=%s&hash=%s' % (
            self.gis_id, self.gis_hash)
        try:
            response = make_get(url_profile)
        except FieldError, e:
            raise e
        else:
            # if response.get('name'): self.name = response.get('name')
            if response.get('contacts'):
                self.contacts = json.dumps(response.get('contacts'))
                # for c in response.get('contacts'):
                #     if c.get('type') == 'phone':
                #        self.contacts+=c.get('value')
            if response.get('schedule'):
                schedule = response.get('schedule', {})
                self.schedule = json.dumps(schedule)
                # schedule = response.get('schedule')
                # ru_day = {'Wed':u'Ср', 'Sun':u'Вскр', 'Fri':u'Птн',
                #     'Tue':u'Вт', 'Mon':u'Пнд', 'Thu':u'Чтв', 'Sat':u'Сб'}
                # week = \
                #    [u'Mon', u'Tue', u'Wed', u'Thu', u'Fri', u'Sat', u'Sun']
                # max_wh = max(
                #    map(lambda s: len(s.values()), schedule.values()))
                # def get_schedule_set(i_list=range(max_wh) ,schedule_set=[]):
                #     if i_list:
                #         i = i_list.pop()
                #         for sch in schedule.values():
                #             wh = sch.get('working_hours-%s'%i,{})
                #             schedule_set.append(
                #                (wh.get(u'from'), wh.get(u'to')))
                #         return get_schedule_set(i_list, schedule_set)
                #     else:
                #         return set(schedule_set)
                # schedule_set = get_schedule_set()
                # if len(schedule_set) == 1:
                #     print list(schedule_set)
                #     schedule_wh = schedule.values()[0]['working_hours-%s'%i]
                #     schedule_format['working_hours-%s'%i] = u"с %s по %s"%(
                #         schedule_wh['from'], schedule_wh['to'])
                #     self.schedule = 'Ежедневно ' + \
                #         ('<br>').join(schedule_format.values())
                # else:
                    # for day, wh in schedule.items():
                    #     schedule[day] = ('<br>').join(
                    #         [u"с %s по %s"%(hours['from'], hours['to']) \
                    #         for hours in wh.values()])
                    # for d in week:
                    #     if schedule.get(d):
                    #         self.schedule = self.schedule + ru_day[d] \
                    #             + ': <br>' + schedule[day] + '<br>'

    def __unicode__(self):
        return self.payment.name + ':' + self.address.get_address()


class Payment(models.Model):
    """Для отображения платежных терминалов"""
    name = models.CharField(
        max_length=256, unique=True,
        verbose_name=u'Название, например \'Терминалы "Симфония"\'')
    description = models.TextField(
        blank=True, null=True, verbose_name=u"Описание, как оплатить")
    marker = models.ForeignKey(
        "MarkerIcon", blank=True,
        verbose_name=u"Иконка маркера на карте", related_name="payments")
    is_terminal = models.BooleanField(
        default=True, verbose_name=u"Отображать в разделе 'Оплата наличными'")
    hint_line = models.CharField(max_length=512, blank=True)
    num = models.IntegerField(null=True, blank=True)

    get_values = lambda self: len(self.points.all())

    get_points = lambda self: self.points.all()

    def __unicode__(self):
        return self.name

    def points_addresses_iterator(self):
        def addresses(points):
            for p in points:
                yield p.address
        return addresses(self.points.iterator())


class MarkerIcon(models.Model):
    name = models.CharField(max_length=256, unique=True)

    get_photo_path = lambda self, filename: os.path.join('icons', filename)

    get_absolute_url = lambda self, host_url='': '%s%s' % (
        host_url, self.ico.url) if self.ico else None
    ico = imagekit_models.ProcessedImageField(
        upload_to=get_photo_path,
        verbose_name=u"иконка", null=True, blank=True, options={'quality': 85},
        processors=[processors.ResizeToFit(100, 100), ]
    )

    width = lambda self: self.ico.width if self.ico else 0
    height = lambda self: self.ico.height if self.ico else 0

    def __unicode__(self):
        return self.name


class StaticPageBase(models.Model):
    class Meta:
        abstract = True
    name = models.CharField(
        max_length=256, unique=True,
        verbose_name=u"Имя. Только латиница",  blank=True)

    display_name = models.CharField(max_length=256, null=True, blank=True)

    get_child = lambda self: None

    get_attach_path = lambda self, filename: 'pages/%s/%s.%s' % (
        self.__class__.__name__.lower(), self.name, filename.split('.')[-1])

    get_url_attach = lambda self, host_url='': '%s%s' % (
        host_url, self.attach.url) if self.attach else None

    attach = models.FileField(
        upload_to=get_attach_path,  null=True, blank=True)

    have_content = lambda self: True if self.content else False

    def __unicode__(self):
        return self.name


class StaticPage(StaticPageBase):
    content = models.TextField(null=True, blank=True)


class TreePage(StaticPageBase):
    class Meta:
        abstract = True

    have_childs = lambda self: True if len(self.get_child()) else False

    def get_child(self):
        childs = getattr(self, '%s_childs' % self.__class__.__name__.lower())
        return list(childs.all())


class DocumentsPage(TreePage):
    content = models.TextField(null=True, blank=True)
    parent = models.ForeignKey(
        'DocumentsPage', null=True, blank=True,
        related_name="%(class)s_childs")


class HelpPage(TreePage):
    content = models.TextField(null=True, blank=True)
    num = models.IntegerField(null=True, blank=True)
    parent = models.ForeignKey(
        'HelpPage', null=True, blank=True, related_name="%(class)s_childs")

    def get_child(self):
        childs = getattr(self, '%s_childs' % self.__class__.__name__.lower())
        return list(childs.all().order_by('num', 'display_name'))


class VacancyPage(TreePage):
    content = models.TextField(
        null=True, blank=True,
        default=u'''\
        <ul>
            <li><span><strong>Должностные обязанности:</strong></span>
                <ul>
                    <li><span>something1</span></li>
                    <li><span>something2</span></li>
                </ul>
            </li>
            <li><span><strong>Требования к кандидатам:</strong></span>
                <ul>
                    <li><span>something1</span></li>
                    <li><span>something2</span></li>
                </ul>
            </li>
        </ul>
        ''')
    parent = models.ForeignKey(
        'VacancyPage', null=True, blank=True, related_name="%(class)s_childs")
    show = models.BooleanField(default=True)

    def get_child(self):
        childs = getattr(self, '%s_childs' % self.__class__.__name__.lower())
        return list(childs.filter(show=True))

    def save(self, *args, **kwargs):
        root = VacancyPage.objects.filter(name='vacancy')
        if not self.__dict__.get('parent_id') and \
                self.name != 'vacancy' and root:
            self.parent = root[0]
        super(VacancyPage, self).save(*args, **kwargs)


# For captcha


class Captcha(models.Model):
    class Meta:
        abstract = True
    key = models.CharField(max_length=256, blank=True)
    date = models.DateTimeField(default=timezone.now(), blank=True)

    get_absolute_url = lambda self, host_url="": host_url + self.img.url

    right = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s:%s" % (self.right, self.get_absolute_url())


class CaptchaImage(Captcha):
    def get_photo_path(self, filename):
        new = "%s.%s" % (uuid.uuid4(), filename.split('.')[-1])
        return os.path.join('captcha', new)
    img = imagekit_models.ProcessedImageField(
        upload_to=get_photo_path, options={'quality': 85},
        processors=[processors.ResizeToFit(100, 100), ]
    )


class CaptchaImageClone(Captcha):
    def get_photo_path(self, filename):
        new = "%s.%s" % (uuid.uuid4(), filename.split('.')[-1])
        return os.path.join('captcha/clone', new)
    img = imagekit_models.ProcessedImageField(
        upload_to=get_photo_path, options={'quality': 85},
        processors=[processors.ResizeToFit(100, 100), ]
    )


# ConnRequest
class ConnRequestManager(models.Manager):
    def sendAll(self):
        map(lambda c: c.send(), self.filter(is_send=False))


class ConnRequest(models.Model):
    fio = models.CharField(max_length=128)
    phone = models.CharField(max_length=128, blank=True)
    email = models.EmailField(max_length=128, blank=True)
    flat = models.CharField(max_length=128)
    address = models.CharField(max_length=128)
    status = models.CharField(max_length=128)
    source = models.CharField(max_length=512, blank=True)
    comment = models.CharField(max_length=512, blank=True)
    is_send = models.BooleanField(default=False)
    is_action = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    date_send = models.DateTimeField(default=None, blank=True)

    objects = ConnRequestManager()

    def send(self):
        address = self.address.split(',')
        second_address = ''
        street = address[0].strip()
        num = address[1].strip() if len(address) > 1 else ''
        building = Building.objects.filter(
            Q(street__name=street, num=num) | Q(street_alt__name=street, num_alt=num)).first()
        if building:
            second_address = building.get_address_alt()
        subject = u'%s (статус дома - %s) %s' % (
            CONN_SPAM['subject'], self.status, u'АКЦИЯ' if self.is_action else u'')
        html = u"""\
                <html>
                  <head>
                  </head>
                  <body>
                    <style type="text/css"> table{color:#FF0}</style>
                    <table>
                    <tbody align="left">
                    <tr>
                        <th width="100" align="left"> Ф.И.О.: </th>
                        <th align="left">%(fio)s</th>
                    </tr>
                    <tr>
                        <th width="100" align="left"> Адрес: </th>
                        <th align="left">%(address)s - %(flat)s</th>
                    </tr>
                    <tr>
                        <th width="100" align="left"> Телефон: </th>
                        <th align="left">%(phone)s</th>
                    </tr>
                    <tr>
                        <th width="100" align="left"> Email: </th>
                        <th align="left">%(email)s</th>
                    </tr>
                    <tr>
                        <th width="100" align="left"> Источник: </th>
                        <th align="left">%(source)s</th>
                    </tr>
                    <tr>
                        <th width="100" align="left"> Комментарий: </th>
                        <th align="left">%(comment)s</th>
                    </tr>
                    </tbody>
                    </table>
                  </body>
                </html>
                """ % {
            'fio': self.fio, 'address': u'%s/%s ' % (self.address, second_address), 'flat': self.flat,
            'phone': self.phone, 'email': self.email,
            'source': self.source, 'comment': self.comment}
        #print second_address
        sendEmail(subject, html)
        self.is_send = True
        self.date_send = timezone.now()
        self.save()

    # def save(self, *args, **kwargs):
    #     super(ConnRequest, self).save(*args, **kwargs)
        # ConnRequest.objects.sendAll()


# Image

class Image(models.Model):
    def get_photo_path(self, filename):
        directory = self.directory or ''
        return os.path.join(directory, filename)

    def get_img_absolute_urls(self, host_url=DEFAULT_IMAGE_HOST_URL):
        return str(host_url) + self.img.url

    name = lambda self: self.img.name

    directory = models.SlugField(
        blank=True, null=True,
        help_text="Directory for save. Image will available by full path:\
        %_SITE_URL_%/media/%_DIRECTORY_%/%_IMAGE_NAME_%")
    img = imagekit_models.ProcessedImageField(
        upload_to=get_photo_path, options={'quality': 85},
    )
    description = models.CharField(max_length=256)

    # Banner cfg
    is_displ = models.BooleanField(
        default=False, help_text="If value is True - image will displayed in \
        a banner on index.html")
    num = models.IntegerField(
        blank=True, null=True, help_text="Order of a display image in the \
        banner. If not num or nums will equals - img will display by date \
        (first in last out).")
    href = models.URLField(blank=True, null=True, )

    def __unicode__(self):
        return self.get_img_absolute_urls()
