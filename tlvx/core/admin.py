# -*- coding: utf-8 -*-
from django.contrib import admin
from tlvx.core.models import *


"""
Объекты
"""


class PaymentPointInline(admin.StackedInline):
    extra = 0
    fieldsets = [
        (None, {'fields': ['address', 'name', 'payment', ]}),
    ]
    model = PaymentPoint


class BuildingAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,
            {'fields': ['street', 'num', 'active', 'plan', 'name', 'co']}),
        (u'Альтернативный адрес',
            {'fields': ['street_alt', 'num_alt'], 'classes': ['collapse']}),
        (u'2gis',
            {'fields': ['lat', 'lng'], 'classes': ['collapse']}),
        (u'Дополнительно',
            {'fields': ['city', 'square', 'date', 'date_in'],
                'classes': ['collapse']}),
    ]
    list_display = ('get_address', 'get_address_alt', 'get_pp', 'square',
                    'co', 'active', 'plan')
    list_editable = ('co', 'square', 'active', 'plan')
    list_filter = ['active', 'plan', 'co', 'date', 'street']
    search_fields = ['street', 'num', 'street_alt', 'num_alt']
    ordering = ('street__name', 'num', 'street_alt__name', 'num_alt')
    #save_on_top = True
    save_as = True
    inlines = [PaymentPointInline]
admin.site.register(Building, BuildingAdmin)


class COAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'schedule', 'contacts',
                    'get_builds_sum', 'marker', 'in_map')
    list_editable = ('marker', 'schedule', 'contacts', 'name', 'in_map')
admin.site.register(CentralOffice, COAdmin)


class SquareAdmin(admin.ModelAdmin):
    list_display = ('num', 'get_builds_sum')
admin.site.register(Square, SquareAdmin)


class StreetAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_builds_sum')
    ordering = ('name', )
admin.site.register(Street, StreetAdmin)


class MarkerIconsAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_absolute_url')
admin.site.register(MarkerIcon, MarkerIconsAdmin)


"""
Динамические страницы
"""


class NoteTAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_notes_sum')
# admin.site.register(NoteType, NoteTAdmin)


class NoteAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,             {'fields': ['header', 'text']}),
        (u'Дополнительно',
            {'fields': ['num', 'date'], 'classes': ['collapse']}),
    ]
    list_display = ('date', 'num', 'header', 'text')
    list_filter = ['date', ]
    list_editable = ('num',)
    search_fields = ['text', 'header']
    filter_horizontal = ['addresses']
    save_as = True
admin.site.register(Note, NoteAdmin)

admin.site.register(RatesType)


class RatesAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['active', 'rtype', 'date_in', 'tables']}),
        (u'Дополнительно', {'fields': ['name'], 'classes': ['collapse']}),
    ]
    list_display = ('date_in', 'date',  'active', 'rtype')
    list_filter = ['date_in', 'date', 'date_out', 'active', 'rtype']
    list_editable = ('active', 'rtype')
    search_fields = ['tables', 'name']
    save_as = True
admin.site.register(Rates, RatesAdmin)


class PaymentPointAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['address', 'name', 'payment']}),
        (u'Дополнительно',
            {'fields': ['schedule', 'contacts'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'get_address', 'payment')
    list_filter = ['payment']
    list_display_links = ('name', 'get_address')
    search_fields = ['address', 'name']
admin.site.register(PaymentPoint, PaymentPointAdmin)


class PaymentAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'is_terminal', 'num',
                           'description', 'marker', 'hint_line']}),
    ]
    list_editable = ('name', 'marker', 'is_terminal', 'hint_line', 'num')
    list_filter = ['is_terminal']
    list_display = ('id', 'name', 'get_values', 'marker', 'is_terminal',
                    'hint_line', 'num')
admin.site.register(Payment, PaymentAdmin)


"""
Статические страницы
"""


class StaticPageAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'display_name', 'attach', 'content']}),
    ]
    list_display = ('id', 'name', 'have_content', 'display_name')
    search_fields = ['display_name', 'name', 'content', 'display_name']
admin.site.register(StaticPage, StaticPageAdmin)


class TreePageChildrenInline(admin.StackedInline):
    extra = 0
    fieldsets = [
        (None, {'fields': ['name', 'display_name', 'attach', ]}),
        (u'Еще', {'fields': ['content'], 'classes': ['collapse']}),
    ]
    verbose_name = u'Потомок'
    verbose_name_plural = u"Потомки"


class TreePageAdmin(StaticPageAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'display_name', 'attach', 'content', ]}),
        (u'Дополнительно', {'fields': ['parent'], 'classes': ['collapse']}),
    ]
    list_display = ('id', 'name', 'display_name', 'have_content', 'parent',
                    'have_childs', 'attach')
    list_editable = ('name', 'parent', 'display_name')


class DocumentsPageChildrenInline(TreePageChildrenInline):
    model = DocumentsPage


class DocumentsPageAdmin(TreePageAdmin):
    inlines = [DocumentsPageChildrenInline]
admin.site.register(DocumentsPage, DocumentsPageAdmin)


class HelpPageChildrenInline(TreePageChildrenInline):
    model = HelpPage


class HelpPageAdmin(TreePageAdmin):
    fieldsets = [
        (None, {'fields':
                ['num', 'name', 'display_name', 'attach', 'content', ]}),
        (u'Дополнительно', {'fields': ['parent'], 'classes': ['collapse']}),
    ]
    list_display = ('id', 'name', 'display_name', 'parent', 'num')
    list_editable = ('name', 'parent', 'display_name', 'num')
    inlines = [HelpPageChildrenInline]
admin.site.register(HelpPage, HelpPageAdmin)


class VacancyPageAdmin(TreePageAdmin):
    list_display = ('id', 'name', 'show', 'display_name',)
    list_editable = ('display_name', 'show', 'name')
    fieldsets = [
        (None, {'fields': ['name', 'show', 'display_name', 'content']}),
        (u'Дополнительно', {'fields': ['attach', ], 'classes': ['collapse']}),
    ]
admin.site.register(VacancyPage, VacancyPageAdmin)


"""
Captcha
"""


class CaptchaAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_absolute_url', 'right', 'key', 'date')
    list_filter = ['right', 'date']
admin.site.register(CaptchaImage, CaptchaAdmin)


class CaptchaCloneAdmin(CaptchaAdmin):
    pass
admin.site.register(CaptchaImageClone, CaptchaCloneAdmin)

"""
Заявки
"""


class ConnRequestAdmin(admin.ModelAdmin):
    list_display = ('address', 'is_send', 'date')
    list_filter = ['is_send', 'date']
admin.site.register(ConnRequest, ConnRequestAdmin)
