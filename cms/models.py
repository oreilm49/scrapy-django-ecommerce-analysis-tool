import datetime
import uuid
from statistics import mean
from typing import Optional, Dict, Union, Type, Iterator, Any
import pandas as pd
from pandas import DataFrame, Series
import requests

from django import forms
from django.contrib.humanize.templatetags import humanize
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import PROTECT, CASCADE, SET_NULL, QuerySet, Q
from django.db.models.fields.json import KeyTextTransform
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField

from cms.constants import MAX_LENGTH, URL_TYPES, SELECTOR_TYPES, TRACKING_FREQUENCIES, ONCE, IMAGE_TYPES, MAIN, \
    THUMBNAIL, WIDGET_CHOICES, WIDGETS, DAILY, PRICE_TIME_PERIODS_LIST, WEEKLY, OPERATORS, OPERATOR_MEAN, \
    SCORING_CHOICES, SCORING_NUMERICAL_HIGHER, SCORING_NUMERICAL_LOWER, SCORING_BOOL_TRUE, SCORING_BOOL_FALSE, \
    EPREL_API_ROOT_URL, ENERGY_LABEL_IMAGE
from cms.serializers import serializers, CustomValueSerializer


def json_data_default() -> Dict[str, None]:
    """
    Default callable for JSONField.
    """
    return {"value": None}


class BaseQuerySet(QuerySet):
    """
    Queryset for base model
    """
    def published(self):
        return self.filter(publish=True)


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
    alternate_names = ArrayField(verbose_name=_("Alternate names"), base_field=models.CharField(max_length=MAX_LENGTH, blank=True), blank=True, null=True, default=list)
    widget = models.CharField(verbose_name=_('widget'), choices=WIDGET_CHOICES, max_length=70, help_text=_("The input widget, which denotes the data type, serializer and deserializer of the unit's corresponding values."))
    repeat = models.CharField(verbose_name=_("Repeat"), max_length=MAX_LENGTH, default=ONCE, choices=TRACKING_FREQUENCIES, help_text=_("The frequency with which this unit should be tracked."), blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def serializer(self) -> CustomValueSerializer:
        return serializers.get(self.field_class)

    @cached_property
    def field_class(self) -> Type[forms.Field]:
        widget_class = self.widget_class
        return WIDGETS[widget_class]

    @cached_property
    def widget_class(self) -> Type[forms.Widget]:
        try:
            return import_string(self.widget)
        except ImportError:
            raise ValueError(_('"{}" is not a valid widget').format(self.widget))

    @cached_property
    def is_bool(self) -> bool:
        return self.widget_class == forms.widgets.CheckboxInput


class Website(BaseModel):
    name = models.CharField(verbose_name=_("Name"), max_length=MAX_LENGTH, help_text=_("The website name"), unique=True)
    domain = models.CharField(verbose_name=_("Domain"), max_length=MAX_LENGTH, help_text=_("The website domain name"), unique=True)
    currency = models.ForeignKey(to=Unit, verbose_name=_("Currency"), on_delete=SET_NULL, blank=True, null=True, help_text=_("The currency this website trades in."), related_name="websites")

    def __str__(self):
        return self.name

    def create_product_attribute(self, product: 'Product', attribute_type: 'AttributeType', value: str) -> 'WebsiteProductAttribute':
        """
        Creates a website product attribute.
        Serializes value using attribute_type unit's serializer before creating product attribute.
        """
        if attribute_type.unit:
            value = attribute_type.unit.serializer.serializer(value)
        return WebsiteProductAttribute.objects.create(website=self, product=product, attribute_type=attribute_type, data={'value': value})


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
    alternate_names = ArrayField(verbose_name=_("Alternate names"), base_field=models.CharField(max_length=MAX_LENGTH, blank=True), null=True, blank=True, default=list)

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

    def custom_get_or_create(self, model: str, category: Category) -> 'Product':
        product_check = self.filter(category=category).filter(
            Q(model=model) |
            Q(alternate_models__contains=[model]),
        )
        if product_check.exists():
            return product_check.first()
        return Product.objects.create(model=model, category=category)

    def brands(self) -> 'ProductAttributeQuerySet':
        return ProductAttribute.objects.filter(product__in=self, attribute_type__name="brand").values_list('data__value', flat=True).distinct('data__value')


class Product(BaseModel):
    model = models.CharField(verbose_name=_("Model"), max_length=MAX_LENGTH, unique=True)
    category = models.ForeignKey(to=Category, verbose_name=_("Category"), on_delete=SET_NULL, blank=True, null=True)
    alternate_models = ArrayField(verbose_name=_("Alternate models"), base_field=models.CharField(max_length=MAX_LENGTH, blank=True), blank=True, null=True, default=list)
    eprel_scraped = models.BooleanField(verbose_name=_("EPREL Scraped"), default=False, help_text=_("Has the EPREL database been scraped for this product?"))
    eprel_code = models.CharField(verbose_name=_("EPREL Code"), max_length=MAX_LENGTH, unique=True, blank=True, null=True)
    eprel_category = models.ForeignKey(to="cms.EprelCategory", verbose_name=_("EPREL Category"), on_delete=SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.model

    objects = ProductQuerySet.as_manager()

    @cached_property
    def image_main_required(self) -> bool:
        return self.images.filter(image_type=MAIN).exists() is False

    @cached_property
    def image_thumb_required(self) -> bool:
        return self.images.filter(image_type=THUMBNAIL).exists() is False

    @cached_property
    def energy_label_required(self) -> bool:
        return self.images.filter(image_type=ENERGY_LABEL_IMAGE).exists() is False

    @property
    def image_main(self):
        image: ProductImage = self.images.filter(image_type=MAIN).first()
        return image.image.url if image else None

    @property
    def image_thumb(self):
        image: ProductImage = self.images.filter(image_type=THUMBNAIL).first()
        return image.image.url if image else None

    @property
    def current_average_price_int(self):
        """avg price of product from most recent price"""
        most_recent_price = self.websiteproductattributes.published().order_by('-created').first()
        if not most_recent_price:
            return None
        prices = self.websiteproductattributes.published().filter(attribute_type__name="price").for_day(most_recent_price.created.date()).values_list('data__value', flat=True)
        return int(mean([float(price) for price in prices])) if prices else None

    @cached_property
    def current_average_price(self) -> Optional[float]:
        """avg price of product from most recent price"""
        price = self.current_average_price_int
        return humanize.intcomma(price) if price else None

    @cached_property
    def brand(self) -> Optional[str]:
        attribute: ProductAttribute = self.productattributes.filter(attribute_type__name="brand").first()
        return attribute.data['value'] if attribute else None

    @cached_property
    def top_attributes(self) -> Iterator[ProductQuerySet]:
        for attribute_config in self.category.category_attribute_configs.order_by('order').iterator():
            attribute_config: 'CategoryAttributeConfig'
            yield attribute_config.attribute_type.productattributes.filter(product__pk=self.pk).first()

    def price_history(self, start_date: datetime.datetime, end_date: Optional[datetime.datetime] = datetime.datetime.now(),
                      time_period: Optional[str] = DAILY, aggregation: Optional[str] = OPERATOR_MEAN, **kwargs) -> Optional[DataFrame]:
        assert time_period in PRICE_TIME_PERIODS_LIST, f"time period must be one of {PRICE_TIME_PERIODS_LIST}"
        assert aggregation in OPERATORS, f"operator must be one of {OPERATORS}"
        price_history = self.websiteproductattributes.published()\
            .filter(created__range=[start_date, end_date], attribute_type__name="price")\
            .annotate(price=KeyTextTransform('value', 'data'))
        if kwargs:
            price_history = price_history.filter(**kwargs)
        df: DataFrame = pd.DataFrame(price_history.values('created', 'price'))
        if not df.get('created'):
            return None
        df_grouper: Series = df['created'].dt.isocalendar().week if time_period == WEEKLY else getattr(df['created'].dt, time_period)
        return getattr(df.groupby(by=df_grouper), aggregation)()

    def get_eprel_api_url(self) -> Optional[str]:
        if not self.eprel_code:
            return
        if self.eprel_category:
            return f"{EPREL_API_ROOT_URL}{self.eprel_category.name}/{self.eprel_code}"
        for eprel_category in self.category.eprel_names.all():
            url = f"{EPREL_API_ROOT_URL}{eprel_category.name}/{self.eprel_code}"
            response = requests.get(url)
            if response.status_code == 200:
                self.eprel_category = eprel_category
                self.save()
                return url


class AttributeTypeQuerySet(BaseQuerySet):

    def custom_get_or_create(self, name: str, unit: Optional[Unit] = None) -> 'AttributeType':
        attribute_type_check = self.filter(Q(name=name) | Q(alternate_names__contains=[name]))
        if attribute_type_check.exists():
            attribute_type: AttributeType = attribute_type_check.first()
            if not attribute_type.unit and unit:
                attribute_type.unit = unit
                attribute_type.save()
            return attribute_type
        return AttributeType.objects.create(name=name, unit=unit)


class AttributeType(BaseModel):
    name = models.CharField(verbose_name=_("Name"), max_length=MAX_LENGTH, unique=True)
    alternate_names = ArrayField(verbose_name=_("Alternate names"), base_field=models.CharField(max_length=MAX_LENGTH, blank=True), null=True, blank=True, default=list)
    unit = models.ForeignKey(to=Unit, verbose_name=_("Data type"), on_delete=SET_NULL, blank=True, null=True, help_text=_("The data type for this attribute"), related_name="attribute_types")

    def __str__(self):
        return self.name

    objects = AttributeTypeQuerySet.as_manager()

    class Meta:
        unique_together = ['name', 'unit']


class BaseProductAttribute(BaseModel):
    product = models.ForeignKey(to=Product, verbose_name=_("Product"), on_delete=CASCADE, related_name="%(class)ss")
    attribute_type = models.ForeignKey(to=AttributeType, verbose_name=_("Data type"), on_delete=SET_NULL, blank=True, null=True, help_text=_("The data type for this attribute"), related_name="%(class)ss")
    data = models.JSONField(verbose_name=_("Data"), help_text=_("The data for this attribute"), null=True, default=json_data_default)

    def __str__(self):
        return f"{self.product.model} > {self.attribute_type}"

    class Meta:
        abstract = True


class ProductAttributeQuerySet(BaseQuerySet):

    def custom_get_or_create(self, product: Product, attribute_type: AttributeType, value: Union[int, str, float, bool, datetime.datetime]) -> 'ProductAttribute':
        """
        Checks if product attribute exists before creating.
        Serializes value using attribute_type unit's serializer before creating product attribute.
        """
        product_attribute_check = self.filter(product=product, attribute_type=attribute_type)
        if product_attribute_check.exists():
            return product_attribute_check.first()
        if attribute_type.unit:
            value = attribute_type.unit.serializer.serializer(value)
        return self.create(product=product, attribute_type=attribute_type, data={'value': value})

    def products(self) -> 'ProductAttributeQuerySet':
        return Product.objects.filter(pk__in=[product_attribute.product.pk for product_attribute in self])


class ProductAttribute(BaseProductAttribute):

    class Meta:
        unique_together = ['product', 'attribute_type']

    objects = ProductAttributeQuerySet.as_manager()

    @property
    def display(self):
        return f"{self.formatted_value} " + f" {self.attribute_type.unit}" if self.attribute_type.unit else ""

    @property
    def formatted_value(self):
        try:
            return humanize.intcomma(int(self.data['value']))
        except Exception:
            return self.data['value']


class WebsiteProductAttributeQuerySet(BaseQuerySet):

    def for_last_day(self) -> QuerySet:
        """returns attribs for the last 24 hours"""
        return self.filter(created__gte=datetime.datetime.now() - datetime.timedelta(hours=24))

    def for_day(self, date: datetime.date) -> QuerySet:
        """returns attribs for specific day"""
        return self.filter(created__date=date)


class WebsiteProductAttribute(BaseProductAttribute):
    website = models.ForeignKey(to=Website, verbose_name=_("Website"), on_delete=CASCADE, related_name="productattributes")

    def __str__(self):
        return f"{self.website} > {self.product} > {self.attribute_type}"

    objects = WebsiteProductAttributeQuerySet.as_manager()


class ProductImage(BaseModel):
    product = models.ForeignKey(to=Product, verbose_name=_("Product"), on_delete=CASCADE, related_name="images")
    image_type = models.CharField(verbose_name=_("Type"), max_length=MAX_LENGTH, choices=IMAGE_TYPES)
    image = models.ImageField(verbose_name=_("image"), upload_to='product_images/')

    def __str__(self):
        return f"{self.product} | {self.image}"


class CategoryAttributeConfig(BaseModel):
    attribute_type = models.ForeignKey(to=AttributeType, verbose_name=_("Attribute"), on_delete=CASCADE, related_name="category_attribute_configs")
    category = models.ForeignKey(to=Category, verbose_name=_("Category"), on_delete=CASCADE, related_name="category_attribute_configs")
    weight = models.IntegerField(verbose_name=_('Weight'))
    company = models.ForeignKey(to="accounts.Company", verbose_name=_("Company"), on_delete=CASCADE, related_name="category_attribute_configs", blank=True, null=True)
    scoring = models.CharField(verbose_name=_("Scoring"), max_length=MAX_LENGTH, choices=SCORING_CHOICES, help_text=_("The mechanism by which values for this attribute should be scored."), blank=True, null=True)

    def __str__(self):
        return f"{self.category} | {self.attribute_type}"

    def product_attribute_data_filter_kwargs(self, value: Union[str, int, float, None]) -> Dict[str, Any]:
        if self.scoring == SCORING_NUMERICAL_HIGHER:
            return {'data__value__gte': value}
        elif self.scoring == SCORING_NUMERICAL_LOWER:
            return {'data__value__lte': value}
        elif self.scoring in [SCORING_BOOL_TRUE, SCORING_BOOL_FALSE]:
            return {'data__value': value}

    @property
    def product_attribute_data_filter_or_exclude(self) -> str:
        if self.scoring == SCORING_BOOL_FALSE:
            return 'exclude'
        return 'filter'

    class Meta:
        unique_together = ['category', 'attribute_type', 'company']


class SpiderResult(BaseModel):
    spider_name = models.CharField(verbose_name=_("spider name"), max_length=MAX_LENGTH)
    website = models.ForeignKey(to="cms.Website", on_delete=SET_NULL, related_name="spider_results", blank=True, null=True)
    category = models.ForeignKey(to="cms.Category", on_delete=SET_NULL, related_name="spider_results", blank=True, null=True)
    items_scraped = models.IntegerField(verbose_name=_("items scraped"), default=0)

    def __str__(self):
        return f"{self.spider_name}: {self.website}: {self.category}"


class EprelCategory(BaseModel):
    category = models.ForeignKey(to="cms.Category", on_delete=SET_NULL, related_name="eprel_names", blank=True, null=True)
    name = models.CharField(verbose_name=_("category name"), max_length=MAX_LENGTH)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = 'category', 'name',
