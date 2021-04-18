from collections import namedtuple
from typing import Union

from dateutil import parser
from django import forms
from pint import UnitRegistry

from cms.constants import FIELD_TYPES

CustomValueSerializer = namedtuple('CustomValueSerializer', ['serializer', 'deserializer'])


def to_float(number: Union[str, int, float]):
    if isinstance(number, float):
        return number
    if isinstance(number, int):
        return float(number)
    return float(UnitRegistry()(number))


serializers = {
    forms.CharField: CustomValueSerializer(
        serializer=str,
        deserializer=str,
    ),
    forms.IntegerField: CustomValueSerializer(
        serializer=int,
        deserializer=int,
    ),
    forms.BooleanField: CustomValueSerializer(
        serializer=bool,
        deserializer=bool,
    ),
    forms.DateTimeField: CustomValueSerializer(
        serializer=lambda value: str(value),
        deserializer=lambda value: parser.parse(value),
    ),
    forms.FloatField: CustomValueSerializer(
        serializer=to_float,
        deserializer=float,
    ),
}
assert set(serializers.keys()) == set(FIELD_TYPES), 'All allowed field types must have serializer data defined'
