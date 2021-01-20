from django.utils.translation import gettext as _

MAX_LENGTH = 100

CATEGORY = _("category")
PRODUCT = _("product")

URL_TYPES = (
    (CATEGORY, _("Category")),
    (PRODUCT, _("Product")),
)

PRICE = _("price")
TABLE = _("table")
IMAGE = _("image")
LINK = _("link")
PAGINATION = _("pagination")

SELECTOR_TYPES = (
    (PRICE, _("Price")),
    (TABLE, _("Table")),
    (IMAGE, _("Image")),
    (LINK, _("Link")),
    (PAGINATION, _("Pagination")),
)

INTEGER = _("int")
FLOAT = _("float")
STRING = _("str")
BOOLEAN = _("bool")

DATA_TYPES = (
    (INTEGER, _("Integer")),
    (FLOAT, _("Float")),
    (STRING, _("String")),
    (BOOLEAN, _("Boolean"))
)
