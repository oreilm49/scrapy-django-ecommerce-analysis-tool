import datetime

from django import forms
from django.test import TestCase
from pint import UnitRegistry, Quantity

from cms.data_processing.constants import Value, UnitValue, RangeUnitValue
from cms.data_processing.units import contains_number, is_range_value, UnitManager, widget_from_type
from cms.form_widgets import FloatInput
from cms.models import Unit
from cms.utils import get_dotted_path


class TestUnits(TestCase):

    def test_contains_number(self):
        self.assertTrue(contains_number("test string 1"))
        self.assertTrue(contains_number("test string 1.00"))
        self.assertFalse(contains_number("test string"))

    def test_is_range_value(self):
        self.assertTrue(is_range_value("200-240"))
        self.assertTrue(is_range_value("200 - 240"))
        self.assertTrue(is_range_value("200 -240"))
        self.assertTrue(is_range_value("200- 240"))
        self.assertFalse(is_range_value("200 240"))
        self.assertFalse(is_range_value("200"))

    def test_widget_from_type(self):
        self.assertEqual(widget_from_type("1"), get_dotted_path(forms.widgets.TextInput))
        self.assertEqual(widget_from_type(1), get_dotted_path(FloatInput))
        self.assertEqual(widget_from_type(True), get_dotted_path(forms.widgets.CheckboxInput))
        self.assertEqual(widget_from_type(datetime.datetime.now()), get_dotted_path(forms.widgets.DateTimeInput))
        self.assertEqual(widget_from_type(1.11), get_dotted_path(FloatInput))

    def test_unit_manager_init(self):
        units: UnitManager = UnitManager()
        self.assertTrue(isinstance(units.ureg, UnitRegistry))

        with self.subTest("aliases"):
            decibel: Quantity = units.ureg("1db")
            self.assertTrue(isinstance(decibel, Quantity))
            self.assertEqual(str(decibel.units), "decibels")

            kilowatt_hour: Quantity = units.ureg("1kwh")
            self.assertTrue(isinstance(kilowatt_hour, Quantity))
            self.assertEqual(str(kilowatt_hour.units), "kilowatt_hour")

            volt: Quantity = units.ureg("1v")
            self.assertTrue(isinstance(volt, Quantity))
            self.assertEqual(str(volt.units), "volt")

            hertz: Quantity = units.ureg("1hz")
            self.assertTrue(isinstance(hertz, Quantity))
            self.assertEqual(str(hertz.units), "hertz")

            watt: Quantity = units.ureg("1w")
            self.assertTrue(isinstance(watt, Quantity))
            self.assertEqual(str(watt.units), "watt")

    def test_get_processed_unit_and_value(self):
        units: UnitManager = UnitManager()
        with self.subTest("str"):
            self.assertEqual(units.get_processed_unit_and_value("str"), Value(value="str"))

        with self.subTest("valid unit"):
            parsed_value: UnitValue = units.get_processed_unit_and_value("1kg")
            kg_unit: Unit = Unit.objects.get(name="kilogram", widget=get_dotted_path(forms.widgets.NumberInput))
            self.assertEqual(parsed_value, UnitValue(value=1, unit=kg_unit))

        with self.subTest("undefined unit"):
            parsed_value: UnitValue = units.get_processed_unit_and_value("1lkj")
            self.assertEqual(parsed_value, Value(value="1lkj"))

        with self.subTest("range value"):
            parsed_value: RangeUnitValue = units.get_processed_unit_and_value("200-240v")
            volt_unit: Unit = Unit.objects.get(name="volt", widget=get_dotted_path(forms.widgets.NumberInput))
            self.assertEqual(parsed_value, RangeUnitValue(unit=volt_unit, value_low=200, value_high=240))

    def test_get_or_create_unit(self):
        units: UnitManager = UnitManager()
        self.assertEqual(units.get_or_create_unit("1"), Value(value=1))

        with self.subTest("unit created"):
            self.assertFalse(Unit.objects.exists())
            parsed_value: UnitValue = units.get_or_create_unit("1kg")
            kg_unit: Unit = Unit.objects.get(name="kilogram", widget=get_dotted_path(forms.widgets.NumberInput))
            self.assertEqual(parsed_value.unit, kg_unit)
            self.assertEqual(parsed_value.value, 1)

        with self.subTest("existing unit - with conversion"):
            parsed_value: UnitValue = units.get_or_create_unit("2000g", unit=kg_unit)
            self.assertEqual(parsed_value.unit, kg_unit)
            self.assertEqual(parsed_value.value, 2)
