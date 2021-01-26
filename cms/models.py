import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import PROTECT, CASCADE, SET_NULL, QuerySet
from django.utils.translation import gettext as _
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField

from cms.constants import MAX_LENGTH, URL_TYPES, SELECTOR_TYPES, DATA_TYPES, TRACKING_FREQUENCIES, ONCE


class BaseQuerySet(QuerySet):
    """
    Queryset for base model
    """


class BaseModel(models.Model):
    order = models.PositiveIntegerField(default=1, verbose_name=_('order'))
    publish = models.BooleanField(default=True, verbose_name=_('publish'))
    uid = models.UUIDField(verbose_name=_('unique id'), help_text=_('Autogenerated unique id for this item in database'), default=uuid.uuid4, editable=False)
    created = CreationDateTimeField(verbose_name=_('creation time'))
    modified = ModificationDateTimeField(verbose_name=_('modification time'))

    objects = BaseQuerySet.as_manager()

    def __str__(self):
        return u'{model_name} ({pk})'.format(
            model_name=self._meta.verbose_name,
            pk=self.pk,
        )

    class Meta:
        abstract = True


class Website(BaseModel):
    name = models.CharField(verbose_name=_("Name"), max_length=MAX_LENGTH, help_text=_("The website name"), unique=True)
    domain = models.CharField(verbose_name=_("Domain"), max_length=MAX_LENGTH, help_text=_("The website domain name"), unique=True)

    def __str__(self):
        return self.name


class Url(BaseModel):
    url = models.CharField(verbose_name=_("Url"), max_length=MAX_LENGTH, help_text=_("The page url"), unique=True)
    url_type = models.CharField(verbose_name=_("Type"), max_length=MAX_LENGTH, choices=URL_TYPES)
    website = models.ForeignKey(to="cms.Website", on_delete=CASCADE, related_name="urls")
    last_scanned = models.DateTimeField(verbose_name=_("Last scanned"), null=True, blank=True)
    category = models.ForeignKey(to="cms.Category", on_delete=SET_NULL, null=True, blank=True, related_name="urls")

    def __str__(self):
        return self.url


class Category(BaseModel):
    name = models.CharField(verbose_name=_("Name"), max_length=MAX_LENGTH, unique=True)
    parent = models.ForeignKey(to="cms.Category", verbose_name=_("Parent"), related_name="sub_categories", on_delete=PROTECT, null=True, blank=True, default=None)
    alternate_names = ArrayField(verbose_name=_("Alternate names"), base_field=models.CharField(max_length=MAX_LENGTH, blank=True), null=True, blank=True)

    def __str__(self):
        return self.name


class Selector(BaseModel):
    selector_type = models.CharField(verbose_name=_("Type"), max_length=MAX_LENGTH, choices=SELECTOR_TYPES)
    css_selector = models.CharField(verbose_name=_("CSS Selector"), max_length=MAX_LENGTH, help_text=_("The CSS selector used to find page data."))
    website = models.ForeignKey(to="cms.Website", on_delete=CASCADE, related_name="selectors")
    regex = models.CharField(verbose_name=_("Regular Expression"), max_length=MAX_LENGTH, help_text=_("A regular expression used to extract data"), null=True, blank=True)
    parent = models.ForeignKey(to="cms.Selector", verbose_name=_("Parent"), related_name="sub_selectors", on_delete=SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class Unit(BaseModel):
    name = models.CharField(verbose_name=_("Name"), max_length=MAX_LENGTH, help_text=_("The unit name"), unique=True)

    def __str__(self):
        return self.name


class PageDataItem(BaseModel):
    name = models.CharField(verbose_name=_("Name"), max_length=MAX_LENGTH, help_text=_("The data item name"))
    data_type = models.CharField(verbose_name=_("Data Type"), max_length=MAX_LENGTH, choices=DATA_TYPES, help_text=_("The data item name"))
    alternate_names = ArrayField(verbose_name=_("Alternate names"), base_field=models.CharField(max_length=MAX_LENGTH, blank=True), blank=True, null=True)
    website = models.ForeignKey(to=Website, related_name="page_data_items", verbose_name=_("Website"), on_delete=SET_NULL, null=True, blank=True, help_text=_("The website this data is specific to: for example, price may vary from website to website. If data isn't website specific, leave blank."))
    selector = models.OneToOneField(to=Selector, verbose_name=_("Selector"), on_delete=SET_NULL, null=True, blank=True, help_text=_("The selector object used to extract page data."))
    unit = models.ForeignKey(to=Unit, verbose_name=_("Unit"), help_text=_("The unit of measurement for this attribute"), on_delete=SET_NULL, null=True, blank=True)
    repeat = models.CharField(verbose_name=_("Repeat"), max_length=MAX_LENGTH, default=ONCE, choices=TRACKING_FREQUENCIES, help_text=_("The frequency with which this data item should be tracked."))

    def __str__(self):
        return self.name


class Product(BaseModel):
    model = models.CharField(verbose_name=_("Model"), max_length=MAX_LENGTH, unique=True)
    category = models.ForeignKey(to=Category, verbose_name=_("Category"), on_delete=SET_NULL, blank=True, null=True)
    alternate_models = ArrayField(verbose_name=_("Alternate models"), base_field=models.CharField(max_length=MAX_LENGTH, blank=True), blank=True, null=True)

    def __str__(self):
        return self.model


class ProductAttribute(BaseModel):
    product = models.ForeignKey(to=Product, verbose_name=_("Product"), on_delete=CASCADE)
    data_type = models.ForeignKey(to=PageDataItem, verbose_name=_("Data type"), on_delete=SET_NULL, blank=True, null=True, help_text=_("The data type for this attribute"))
    value = models.CharField(verbose_name=_("Value"), max_length=MAX_LENGTH, help_text=_("The value for this attribute"))

    def __str__(self):
        return f"{self.product.model} > {self.data_type}"

    class Meta:
        unique_together = ['product', 'data_type']
