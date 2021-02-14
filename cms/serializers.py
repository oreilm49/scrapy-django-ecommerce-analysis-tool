from collections import namedtuple

from dateutil import parser
from django import forms

from cms.constants import FIELD_TYPES

CustomValueSerializer = namedtuple('CustomValueSerializer', ['serializer', 'deserializer'])

custom_fields = {
    forms.CharField: CustomValueSerializer(
        serializer=str,
        deserializer=str,
    ),
    forms.IntegerField: CustomValueSerializer(
        serializer=int,
        deserializer=int,
    ),
    forms.BooleanField: CustomValueSerializer(
        serializer=lambda value: bool,
        deserializer=lambda value: bool,
    ),
    forms.DateTimeField: CustomValueSerializer(
        serializer=lambda value: str(value),
        deserializer=lambda value: parser.parse(value),
    ),
    forms.FloatField: CustomValueSerializer(
        serializer=lambda value: float,
        deserializer=lambda value: float,
    ),
}
assert set(custom_fields.keys()) == set(FIELD_TYPES), 'All allowed field types must have serializer data defined'

