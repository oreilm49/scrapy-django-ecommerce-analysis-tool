import datetime
import re
from typing import Optional, Union, List

from django import forms
from pint import UnitRegistry, Quantity, errors

from cms.data_processing.constants import UnitValue, Value, RangeUnitValue
from cms.data_processing.errors import UnhandledDefinitionSyntaxError
from cms.form_widgets import FloatInput
from cms.models import Unit
from cms.utils import get_dotted_path


def contains_number(value: Union[str, float, int]) -> bool:
    if isinstance(value, (float, int)):
        return True
    return True if next((character for character in value if character.isdigit()), None) else False


def is_range_value(value: str) -> bool:
    return len(value.split("-")) == 2


def is_bool_value(value: str) -> bool:
    return value.strip().lower() in ["true", "yes", "y"]


def widget_from_type(data: Union[int, float, str, bool, datetime.datetime]):
    if isinstance(data, str):
        return get_dotted_path(forms.widgets.TextInput)
    elif isinstance(data, bool):
        return get_dotted_path(forms.widgets.CheckboxInput)
    elif isinstance(data, int) or isinstance(data, float):
        return get_dotted_path(FloatInput)
    elif isinstance(data, datetime.datetime):
        return get_dotted_path(forms.widgets.DateTimeInput)


class UnitManager:

    def __init__(self) -> None:
        super().__init__()
        self.ureg = UnitRegistry()
        self.ureg.define('decibels = 1 * decibel = db')
        self.ureg.define('kilowatt_hour = 3600 * kilojoules = kwh')
        self.ureg.define("@alias volt = v")
        self.ureg.define("@alias hertz = hz")
        self.ureg.define("@alias watt = w")
        self.ureg.define('programmes = 1 * program = programmes')
        self.regex_digit_patterns = [r"\d* year"]

    def get_processed_unit_and_value(self, value: str, unit: Optional[Unit] = None) -> Union[UnitValue, Value, RangeUnitValue]:
        try:
            if not contains_number(value):
                if is_bool_value(value):
                    bool_unit, _ = Unit.objects.get_or_create(name="bool", widget=widget_from_type(True))
                    return UnitValue(unit=bool_unit, value=True)
                return Value(value=value)
            return self.get_or_create_unit(value, unit=unit)
        except errors.UndefinedUnitError:
            for pattern in self.regex_digit_patterns:
                match: re.Match = re.search(pattern, value)
                if match:
                    return self.get_or_create_unit(match.group(), unit=unit)
            return Value(value=value)
        except AttributeError:
            return Value(value=value)
        except (errors.DefinitionSyntaxError, errors.DimensionalityError):
            if is_range_value(value):
                values: List[str] = value.split("-")
                low: Union[UnitValue, Value] = self.get_or_create_unit(values[0].strip(), unit=unit)
                high: Union[UnitValue, Value] = self.get_or_create_unit(values[1].strip(), unit=unit)
                range_unit: Unit = high.unit if isinstance(high, UnitValue) else low.unit
                return RangeUnitValue(unit=range_unit, value_low=low.value, value_high=high.value)
            raise UnhandledDefinitionSyntaxError

    def get_or_create_unit(self, value: str, unit: Optional[Unit] = None):
        quantity: Union[Quantity, int] = self.ureg(value)
        if isinstance(quantity, int):
            return Value(value=quantity)
        name: str = str(quantity.units)
        value: Union[str, int, float] = quantity.magnitude
        if unit:
            # if pre existing unit has different type to new data,
            # convert new data to type of unit
            if unit.name is not name:
                quantity: Quantity = quantity.to(unit.name)
                value: Union[str, int, float] = quantity.magnitude
        else:
            unit, _ = Unit.objects.get_or_create(name=name, widget=widget_from_type(value))
        return UnitValue(unit=unit, value=value)
