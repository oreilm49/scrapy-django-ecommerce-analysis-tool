from collections import namedtuple

ProcessedAttribute = namedtuple("ProcessedAttribute", ["attribute_type", "unit", "amount"])
UnitValue = namedtuple("UnitValue", ["unit", "value"])
Value = namedtuple("Value", ["value"])
