import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import PROTECT, CASCADE, SET_NULL, QuerySet, Q
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField

from cms.constants import MAX_LENGTH, URL_TYPES, SELECTOR_TYPES, DATA_TYPES, TRACKING_FREQUENCIES, ONCE, IMAGE_TYPES, \
    MAIN, THUMBNAIL


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


class Unit(BaseModel):
    name = models.CharField(verbose_name=_("Name"), max_length=MAX_LENGTH, help_text=_("The unit name"), unique=True)
    alternate_names = ArrayField(verbose_name=_("Alternate names"), base_field=models.CharField(max_length=MAX_LENGTH, blank=True), blank=True, null=True)
    data_type = models.CharField(verbose_name=_("Data Type"), max_length=MAX_LENGTH, choices=DATA_TYPES, help_text=_("The data type of the unit"), blank=True, null=True)
    repeat = models.CharField(verbose_name=_("Repeat"), max_length=MAX_LENGTH, default=ONCE, choices=TRACKING_FREQUENCIES, help_text=_("The frequency with which this unit should be tracked."), blank=True, null=True)

    def __str__(self):
        return self.name


class Website(BaseModel):
    name = models.CharField(verbose_name=_("Name"), max_length=MAX_LENGTH, help_text=_("The website name"), unique=True)
    domain = models.CharField(verbose_name=_("Domain"), max_length=MAX_LENGTH, help_text=_("The website domain name"), unique=True)
    currency = models.ForeignKey(to=Unit, verbose_name=_("Currency"), on_delete=SET_NULL, blank=True, null=True, help_text=_("The currency this website trades in."), related_name="websites")

    def __str__(self):
        return self.name

    def create_product_attribute(self, product: 'Product', attribute_type: 'AttributeType', value: str) -> 'WebsiteProductAttribute':
        return WebsiteProductAttribute.objects.create(website=self, product=product, attribute_type=attribute_type, value=value)


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
        return f"{self.website} - {self.selector_type}"


class ProductQuerySet(BaseQuerySet):

    def get_or_create_for_item(self, item: 'ProductPageItem') -> 'Product':
        product_check = self.filter(
            Q(model=item['model']) |
            Q(alternate_models__contains=[item['model']]),
            category=item['category']
        )
        if product_check.exists():
            return product_check.first()
        return Product.objects.create(model=item['model'], category=item['category'])


class Product(BaseModel):
    model = models.CharField(verbose_name=_("Model"), max_length=MAX_LENGTH, unique=True)
    category = models.ForeignKey(to=Category, verbose_name=_("Category"), on_delete=SET_NULL, blank=True, null=True)
    alternate_models = ArrayField(verbose_name=_("Alternate models"), base_field=models.CharField(max_length=MAX_LENGTH, blank=True), blank=True, null=True)

    def __str__(self):
        return self.model

    objects = ProductQuerySet.as_manager()


class AttributeTypeQuerySet(BaseQuerySet):

    def get_or_create_by_name(self, name: str) -> 'AttributeType':
        attribute_type_check = self.filter(Q(name=name) | Q(alternate_names__contains=[name]))
        if attribute_type_check.exists():
            return attribute_type_check.first()
        return AttributeType.objects.create(name=name)


class AttributeType(BaseModel):
    name = models.CharField(verbose_name=_("Name"), max_length=MAX_LENGTH, unique=True)
    alternate_names = ArrayField(verbose_name=_("Alternate names"), base_field=models.CharField(max_length=MAX_LENGTH, blank=True), null=True, blank=True)
    unit = models.ForeignKey(to=Unit, verbose_name=_("Data type"), on_delete=SET_NULL, blank=True, null=True, help_text=_("The data type for this attribute"), related_name="attribute_types")

    def __str__(self):
        return f"{self.name} > {self.unit}"

    objects = AttributeTypeQuerySet.as_manager()

    class Meta:
        unique_together = ['name', 'unit']


class BaseProductAttribute(BaseModel):
    product = models.ForeignKey(to=Product, verbose_name=_("Product"), on_delete=CASCADE, related_name="%(class)s")
    attribute_type = models.ForeignKey(to=AttributeType, verbose_name=_("Data type"), on_delete=SET_NULL, blank=True, null=True, help_text=_("The data type for this attribute"), related_name="%(class)s")
    value = models.CharField(verbose_name=_("Value"), max_length=MAX_LENGTH, help_text=_("The value for this attribute"))

    def __str__(self):
        return f"{self.product.model} > {self.attribute_type}"

    class Meta:
        abstract = True


class ProductAttribute(BaseProductAttribute):

    class Meta:
        unique_together = ['product', 'attribute_type']


class WebsiteProductAttribute(BaseProductAttribute):
    website = models.ForeignKey(to=Website, verbose_name=_("Website"), on_delete=CASCADE, related_name="product_attributes")

    def __str__(self):
        return f"{self.website} > {self.product} > {self.attribute_type}"


class ProductImage(BaseModel):
    product = models.ForeignKey(to=Product, verbose_name=_("Product"), on_delete=CASCADE, related_name="images")
    image_type = models.CharField(verbose_name=_("Type"), max_length=MAX_LENGTH, choices=IMAGE_TYPES)
    image = models.FilePathField(verbose_name=_("image"))

    def __str__(self):
        return f"{self.product} | {self.image}"
