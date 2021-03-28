from collections import OrderedDict
from typing import Dict, Type

from django import forms
from django.utils.translation import gettext as _

from cms.form_widgets import FloatInput
from cms.utils import get_dotted_path

MAX_LENGTH = 100

CATEGORY = "category"
PRODUCT = "product"

URL_TYPES = (
    (CATEGORY, _("Category")),
    (PRODUCT, _("Product")),
)

MODEL = "model"
PRICE = "price"
TEXT = "text"
TABLE = "table"
IMAGE = "image"
LINK = "link"
PAGINATION = "pagination"
TABLE_VALUE_COLUMN = "table_value_column"
TABLE_VALUE_COLUMN_BOOL = "table_value_column_bool"
TABLE_LABEL_COLUMN = "table_label_column"

SELECTOR_TYPES = (
    (MODEL, _("Model")),
    (PRICE, _("Price")),
    (TEXT, _("Text")),
    (TABLE, _("Table")),
    (IMAGE, _("Image")),
    (LINK, _("Link")),
    (PAGINATION, _("Pagination")),
    (TABLE_VALUE_COLUMN, _("Table Value Column")),
    (TABLE_VALUE_COLUMN_BOOL, _("Table Value Column Bool")),
    (TABLE_LABEL_COLUMN, _("Table Label Column")),
)


ONCE = 'once'
HOURLY = 'hour'
DAILY = 'day'
WEEKLY = 'week'
MONTHLY = 'month'

TRACKING_FREQUENCIES = (
    (ONCE, _('Once')),
    (HOURLY, _('Hourly')),
    (DAILY, _('Daily')),
    (WEEKLY, _('Weekly')),
    (MONTHLY, _('Monthly')),
)

PRICE_TIME_PERIODS_LIST = [p[0] for p in TRACKING_FREQUENCIES[1:]]

MAIN = "main"
THUMBNAIL = "thumbnail"

IMAGE_TYPES = (
    (MAIN, _("Main")),
    (THUMBNAIL, _("Thumbnail")),
)

# Dictionary of supported widgets mapped to form field class
WIDGETS: Dict[Type[forms.Widget], Type[forms.Field]] = OrderedDict([
    (forms.widgets.TextInput, forms.CharField),
    (forms.widgets.NumberInput, forms.IntegerField),
    (FloatInput, forms.FloatField),
    (forms.widgets.CheckboxInput, forms.BooleanField),
    (forms.widgets.DateTimeInput, forms.DateTimeField),
])

# Set of supported field type classes
FIELD_TYPES = set(WIDGETS.values())

WIDGET_NAMES = {
    forms.widgets.TextInput: _("Text"),
    forms.widgets.NumberInput: _("Number (integer)"),
    forms.widgets.CheckboxInput: _("Checkbox"),
    forms.widgets.DateTimeInput: _("Date & Time"),
    FloatInput: _("Number (decimal)"),
}

WIDGET_CHOICES = [(get_dotted_path(cls), WIDGET_NAMES.get(cls, cls.__name__)) for cls in WIDGETS.keys()]

OPERATOR_MEAN = 'mean'
OPERATOR_MAX = 'max'
OPERATOR_MIN = 'min'
OPERATOR_SUM = 'sum'

OPERATORS = (OPERATOR_MEAN, OPERATOR_MAX, OPERATOR_MIN, OPERATOR_SUM)
