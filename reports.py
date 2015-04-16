#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import xlwt
from django.core.exceptions import ObjectDoesNotExist

COL_WIDTH = 9000
font0 = xlwt.Font()
font0.bold = True
font0.height = 270

style0 = xlwt.XFStyle()
style0.font = font0


class Report(object):
    WB_NAME = ''

    """docstring for Report"""
    def __init__(self, email):
        self.wb = xlwt.Workbook()
        self.email = email
        if self.email is None:
            self.email = CONN_SPAM['reports']

    def _write_bld_to_ws(self, ws_name, buildings):
        def write_bld_to_xls((i, bld)):
            ws.write(i+1, 0, bld.get_address())
            ws.write(i+1, 1, bld.get_address_alt())

        ws = self.wb.add_sheet(ws_name)
        ws.write(0, 0, 'Address', style0)
        ws.write(0, 1, 'Second Address', style0)
        map(write_bld_to_xls, enumerate(buildings))
        ws.col(0).width = COL_WIDTH
        ws.col(1).width = COL_WIDTH

    def _create_wb(self):
        pass

    def send_report(self):
        if self.WB_NAME:
            self._create_wb()
            self.wb.save(self.WB_NAME)
            sendEmail(attach=self.WB_NAME, to=self.email)


class ReportBuilding(Report):
    """send report about connection/planing" buildings on email"""

    WB_NAME = 'buildings.xls'

    def __init__(self, email):
        super(ReportBuilding, self).__init__(email)

    def _write_active(self):
        self._write_bld_to_ws(
            'Active', Building.objects.get_is_active_iterator())

    def _write_plan(self):
        self._write_bld_to_ws(
            'In Plan', Building.objects.get_in_plan_iterator())

    def _create_wb(self):
        self._write_active()
        self._write_plan()


class ReportPayment(Report):
    """send report about symphony paymeent points"""

    WB_NAME = 'payment.xls'

    def __init__(self, email, name=None):
        super(ReportPayment, self).__init__(email)
        name = name or u'Симфония'
        try:
            self.payment = Payment.objects.get(name=name)
            self.WB_NAME = '%s-%s' % (name, self.WB_NAME)
        except ObjectDoesNotExist:
            print "Unknown name %s for payment object" % name
            sys.exit()

    def _create_wb(self):
        self._write_bld_to_ws(
            u'Terminals', self.payment.points_addresses_iterator())


def report_buildings(email):
    ReportBuilding(email).send_report()


def report_terminals(email, name=None):
    ReportPayment(email, name).send_report()


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tlvx.settings")

    from tlvx.helpers import sendEmail
    from tlvx.settings import CONN_SPAM
    from tlvx.core.models import Building, Payment

    argv = sys.argv
    email = argv[1] if len(argv) > 1 else None

    report_buildings(email)
    report_terminals(email)
