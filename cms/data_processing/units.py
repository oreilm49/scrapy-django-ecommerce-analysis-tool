from typing import Optional, Union

from pint import UnitRegistry, Quantity, errors

from cms.data_processing.constants import UnitValue, Value
from cms.models import Unit


class UnitManager(UnitRegistry):

    def __init__(self, filename="", force_ndarray=False, force_ndarray_like=False, default_as_delta=True,
                 autoconvert_offset_to_baseunit=False, on_redefinition="warn", system=None,
                 auto_reduce_dimensions=False, preprocessors=None, fmt_locale=None, non_int_type=float,
                 case_sensitive=True):
        super().__init__(filename, force_ndarray, force_ndarray_like, default_as_delta, autoconvert_offset_to_baseunit,
                         on_redefinition, system, auto_reduce_dimensions, preprocessors, fmt_locale, non_int_type,
                         case_sensitive)
        self.define('decibels = 1 * decibel = db')
        self.define('@alias kilowatt_hour = kwh')
        self.define('@alias ampere = a')

    def get_processed_unit_and_value(self, value: str, unit: Optional[Unit] = None) -> Union[UnitValue, Value]:
        try:
            quantity: Union[Quantity, int] = self(value)
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
        except errors.UndefinedUnitError as e:
            return Value(value=value)
