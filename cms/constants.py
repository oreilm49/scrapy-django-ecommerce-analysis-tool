from django.utils.translation import gettext as _

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
    (TABLE_LABEL_COLUMN, _("Table Label Column")),
)

INTEGER = "int"
FLOAT = "float"
STRING = "str"
BOOLEAN = "bool"

DATA_TYPES = (
    (INTEGER, _("Integer")),
    (FLOAT, _("Float")),
    (STRING, _("String")),
    (BOOLEAN, _("Boolean"))
)

ONCE = 'once'
HOURLY = 'hourly'
DAILY = 'daily'
WEEKLY = 'weekly'
MONTHLY = 'monthly'

TRACKING_FREQUENCIES = (
    (ONCE, _('Once')),
    (HOURLY, _('Hourly')),
    (DAILY, _('Daily')),
    (WEEKLY, _('Weekly')),
    (MONTHLY, _('Monthly')),
)

MAIN = "main"
THUMBNAIL = "thumbnail"

IMAGE_TYPES = (
    (MAIN, _("Main")),
    (THUMBNAIL, _("Thumbnail")),
)
