# -*- coding: utf-8 -*-
from tlvx.tests import MainTest

from django.test import TestCase
from tlvx.core.models import *

# class GisTest(TestCase):
#     pass

# class BuildingTest(TestCase):
#     def setUp(self):
#         street = Street.objects.get_or_create(name=u'Кантемирова')[0]
#         self.building = Building.objects.get_or_create(num=23,street=street)[0]
#     def test_create(self):
#         """
#         Создаем строение, с параметрами <Street>, num
#         Должно создасться место в городе Благовещенске, не активное, жилое
#         """
#         self.assertEqual(Building.objects.get(id=self.building.id).city.name,u'Благовещенск')
#         self.assertEqual(Building.objects.get(id=self.building.id).btype.name,'house')
#         self.assertFalse(Building.objects.get(id=self.building.id).active)
#     def test_double(self):
#         """
#         Место с таким же сочетанием улица/дом не должно создаваться
#         """
#         double = Building.objects.create(
#             street=self.building.street, num=self.building.num)
#         self.assertEqual(
#             Building.objects.filter(
#                 street=self.building.street, num=self.building.num).count(),
#             1
#         )
#     def test_active(self):
#         """
#         Сначала устанавливаем plan в True и сохраняем, 
#         проверяем,что active=false, date_in = none.
#         потом устанавливаем active в True и сохраняем.
#         plan должен стать false и date_in - текущим временем
#         """
#         self.building.plan = True
#         self.building.save()
#         self.assertTrue(Building.objects.get(id=self.building.id).plan)
#         self.assertFalse(Building.objects.get(id=self.building.id).active)
#         self.assertFalse(Building.objects.get(id=self.building.id).date_in)
#         self.building.active = True
#         self.building.save()
#         self.assertTrue(Building.objects.get(id=self.building.id).active)
#         self.assertFalse(Building.objects.get(id=self.building.id).plan)
#         self.assertTrue(Building.objects.get(id=self.building.id).date_in)

# class RatesTest(TestCase):
#     def setUp(self):
#         self.rates = Rates.objects.get_or_create(
#             name='rates', tables='table', active=True)[0]
#     def test_create(self):
#         """
#         Создаем объект с active=True.
#         date_in должен быть текущее время,
#         rtype должен быть p (физики)
#         """
#         self.assertEqual(self.rates.rtype.name, 'p')
#         self.assertTrue(self.rates.date_in)
#     def test_active(self):
#         """
#         Меняем active на false.
#         date_out должен быть текущее время
#         """
#         self.assertFalse(Rates.objects.get(id=self.rates.id).date_out)
#         self.rates.active = False
#         self.rates.save()
#         self.assertFalse(Rates.objects.get(id=self.rates.id).active)
#         self.assertTrue(Rates.objects.get(id=self.rates.id).date_out)
