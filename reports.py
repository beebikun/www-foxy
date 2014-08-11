#!/usr/bin/env python
import os
import sys
import xlwt

COL_WIDTH = 9000
WB_NAME = 'buildings.xls'
font0 = xlwt.Font()
font0.bold = True
font0.height = 270

style0 = xlwt.XFStyle()
style0.font = font0


class ReportBuilding(object):
    """send report about connection/planing" buildings on email"""
    def __init__(self, email):
        super(ReportBuilding, self).__init__()
        self.wb = xlwt.Workbook()
        self.email = email
        if self.email is None:
            self.email = CONN_SPAM['reports']

    def __write_bld_to_ws(self, ws_name, buildings):
        def write_bld_to_xls((i, bld)):
            ws.write(i+1, 0, bld.get_address())
            ws.write(i+1, 1, bld.get_address_alt())

        ws = self.wb.add_sheet(ws_name)
        ws.write(0, 0, 'Address', style0)
        ws.write(0, 1, 'Second Address', style0)
        map(write_bld_to_xls, enumerate(buildings))
        ws.col(0).width = COL_WIDTH
        ws.col(1).width = COL_WIDTH

    def _write_active(self):
        self.__write_bld_to_ws(
            'Active', Building.objects.get_is_active_iterator())

    def _write_plan(self):
        self.__write_bld_to_ws(
            'In Plan', Building.objects.get_in_plan_iterator())

    def _create_wb(self):
        self._write_active()
        self._write_plan()
        self.wb.save(WB_NAME)

    def send_report(self):
        self._create_wb()
        sendEmail(attach=WB_NAME, to=self.email)


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tlvx.settings")

    from tlvx.core.models import Building
    from tlvx.helpers import sendEmail
    from tlvx.settings import CONN_SPAM

    argv = sys.argv
    ReportBuilding(argv[1] if len(argv) > 1 else None).send_report()
