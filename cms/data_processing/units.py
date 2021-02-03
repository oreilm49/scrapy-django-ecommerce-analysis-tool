from typing import Optional, Union, List

from pint import UnitRegistry, Quantity, errors

from cms.data_processing.constants import UnitValue, Value, RangeUnitValue
from cms.data_processing.errors import UnhandledDefinitionSyntaxError
from cms.models import Unit


def contains_number(value: str) -> bool:
    return True if next((character for character in value if character.isdigit()), None) else False


def is_range_value(value: str) -> bool:
    return len(value.split("-")) == 2


class UnitManager:

    def __init__(self) -> None:
        super().__init__()
        self.ureg = UnitRegistry()
        self.ureg.define('decibels = 1 * decibel = db')
        self.ureg.define('kilowatt_hour = 3600 * kilojoules = kwh')
        self.ureg.define("@alias volt = v")
        self.ureg.define("@alias hertz = hz")
        self.ureg.define("@alias watt = w")

    def get_processed_unit_and_value(self, value: str, unit: Optional[Unit] = None) -> Union[UnitValue, Value, RangeUnitValue]:
        try:
            if not contains_number(value):
                return Value(value=value)
            return self.get_or_create_unit(value, unit=unit)
        except errors.UndefinedUnitError:
            return Value(value=value)
        except AttributeError:
            return Value(value=value)
        except (errors.DefinitionSyntaxError, errors.DimensionalityError):
            if is_range_value(value):
                values: List[str] = value.split("-")
                low: Union[UnitValue, Value] = self.get_or_create_unit(values[0], unit=unit)
                high: Union[UnitValue, Value] = self.get_or_create_unit(values[1], unit=unit)
                range_unit: Unit = high.unit if isinstance(high, UnitValue) else low.unit
                return RangeUnitValue(unit=range_unit, value_low=low.value, value_high=high.value)
            raise UnhandledDefinitionSyntaxError

    def get_or_create_unit(self, value: str, unit: Optional[Unit] = None):
        quantity: Union[Quantity, int] = self.ureg(value)
        if isinstance(quantity, int):
            return Value(value=value)
        name: str = str(quantity.units)
        value: Union[str, int, float] = quantity.magnitude
        if unit:
            if unit.name is not name:
                quantity: Quantity = quantity.to(unit.name)
                value: Union[str, int, float] = quantity.magnitude
        else:
            unit, _ = Unit.objects.get_or_create(name=name)
        return UnitValue(unit=unit, value=value)
