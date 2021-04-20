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
ENERGY_LABEL_PDF = 'energy_label_pdf'
ENERGY_LABEL_IMAGE = 'energy_label_img'
ENERGY_LABEL_QR = 'energy_label_qr'
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
    (ENERGY_LABEL_PDF, _("Energy Label PDF")),
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
YEARLY = 'year'

TRACKING_FREQUENCIES = (
    (ONCE, _('Once')),
    (HOURLY, _('Hourly')),
    (DAILY, _('Daily')),
    (WEEKLY, _('Weekly')),
    (MONTHLY, _('Monthly')),
    (YEARLY, _('Yearly')),
)

PRICE_TIME_PERIODS_LIST = [p[0] for p in TRACKING_FREQUENCIES[1:]]

MAIN = "main"
THUMBNAIL = "thumbnail"

IMAGE_TYPES = (
    (MAIN, _("Main")),
    (THUMBNAIL, _("Thumbnail")),
    (ENERGY_LABEL_IMAGE, _("Energy Label")),
    (ENERGY_LABEL_QR, _("Energy Label QR")),
)

SCORING_NUMERICAL_HIGHER = 'higher'
SCORING_NUMERICAL_LOWER = 'lower'
SCORING_BOOL_TRUE = 'true'
SCORING_BOOL_FALSE = 'false'

SCORING_CHOICES = (
    (SCORING_NUMERICAL_HIGHER, _("Higher number value")),
    (SCORING_NUMERICAL_LOWER, _("Lower number value")),
    (SCORING_BOOL_TRUE, _("True boolean value")),
    (SCORING_BOOL_FALSE, _("False boolean value")),
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

EPREL_API_ROOT_URL = 'https://eprel.ec.europa.eu/api/products/'

WEBSITE_TYPE_RETAILER = 'retailer'
WEBSITE_TYPE_SUPPLIER = 'supplier'
WEBSITE_TYPES = (
    (WEBSITE_TYPE_RETAILER, _('Retailer')),
    (WEBSITE_TYPE_SUPPLIER, _('Supplier')),
)
