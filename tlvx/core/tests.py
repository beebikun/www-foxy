# -*- coding: utf-8 -*-
from django.core.exceptions import FieldError
from django.test import TestCase
from tlvx.core import models
from tlvx.tests import _rnd_float


class BuildingTest(TestCase):
    def setUp(self):
        street = models.Street.objects.get_or_create(name=u'Кантемирова')[0]
        self.b = models.Building.objects.get_or_create(
            num=models.Building.objects.all().count(), street=street,
            lat=_rnd_float(), lng=_rnd_float())[0]

    def test_create(self):
        """
        Создаем строение, с параметрами <Street>, num
        Должно создасться место в городе Благовещенске, не активное, жилое
        """
        self.assertEqual(self.b.city.name, u'Благовещенск')
        self.assertEqual(self.b.btype.name, 'house')
        self.assertFalse(self.b.active)

    def test_double(self):
        """
        Место с таким же сочетанием улица/дом не должно создаваться
        """
        _create_double = lambda: models.Building.objects.create(**params)
        params = dict(street=self.b.street, num=self.b.num)
        self.assertRaises(FieldError, _create_double)
        self.assertEqual(models.Building.objects.filter(**params).count(), 1)

    def test_active(self):
        """
        Сначала устанавливаем plan в True и сохраняем,
        проверяем,что active=false, date_in = none.
        потом устанавливаем active в True и сохраняем.
        plan должен стать false и date_in - текущим временем
        """
        self.b.plan = True
        self.b.save()
        self.assertTrue(models.Building.objects.get(id=self.b.id).plan)
        self.assertFalse(models.Building.objects.get(id=self.b.id).active)
        self.assertFalse(models.Building.objects.get(id=self.b.id).date_in)
        self.b.active = True
        self.b.save()
        self.assertTrue(models.Building.objects.get(id=self.b.id).active)
        self.assertFalse(models.Building.objects.get(id=self.b.id).plan)
        self.assertTrue(models.Building.objects.get(id=self.b.id).date_in)


class RatesTest(TestCase):
    def _get_selfr(self):
        return models.Rates.objects.get(id=self.rates.id)

    def _activate_self(self, val=True):
        self.rates.active = val
        self.rates.save()

    def setUp(self):
        self.rates = models.Rates.objects.get_or_create(
            name='rates', tables='table', active=True)[0]

    def test_create(self):
        """
        Создаем объект с active=True.
        date_in должен быть текущее время,
        rtype должен быть p (физики)
        """
        self.assertEqual(self.rates.rtype.name, 'p')
        self.assertTrue(self.rates.date_in)

    def test_create_with_other_type(self):
        other = models.Rates.objects.get_or_create(
            name='other', tables='table', active=True,
            rtype=models.RatesType.objects.get_or_create(name='jp')[0])[0]
        self.assertTrue(other.active)
        self.assertTrue(self._get_selfr().active)
        self.assertEqual(other.rtype.name, 'jp')

    def test_active(self):
        """
        Меняем active на false.
        date_out должен быть текущее время
        """
        self.assertFalse(models.Rates.objects.get(id=self.rates.id).date_out)
        self._activate_self(False)
        self.assertFalse(self._get_selfr().active)
        self.assertTrue(self._get_selfr().date_out)

    def test_second_active(self):
        self._activate_self()
        self.assertTrue(self._get_selfr().active)
        second_active = models.Rates.objects.get_or_create(
            name='rates2', tables='table', active=True)[0]
        self.assertTrue(second_active.active)
        self.assertFalse(self._get_selfr().active)
