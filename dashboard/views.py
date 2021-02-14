import itertools

from django.views.generic import TemplateView

from cms.forms import CategoryTableForm
from cms.models import Product
from cms.utils import products_grouper


class CategoryLineUp(TemplateView):
    template_name = 'views/category_line_up.html'

    def get_form(self):
        return CategoryTableForm(self.request.GET or None)

    def get_context_data(self, **kwargs):
        data: dict = super().get_context_data(**kwargs)
        form: CategoryTableForm = self.get_form()
        data.update(form=self.get_form())
        if self.request.GET:
            if form.is_valid():
                products = form.search(Product.objects.published())
                data.update(
                    x_axis_groups=itertools.groupby(products.iterator(), key=lambda product: products_grouper(
                        product,
                        form.x_axis_attribute,
                        form.x_axis_values
                    )),
                    y_axis_groups=form.y_axis_values,
                )
                return data
        return data
