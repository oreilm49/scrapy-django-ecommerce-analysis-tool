from typing import List, Optional, Dict

from bokeh.embed import components
from bokeh.plotting import figure, ColumnDataSource
from pandas import DataFrame

from cms.models import ProductAttribute


def get_brands() -> List[Optional[str]]:
    return ProductAttribute.objects.filter(attribute_type__name="brand").values_list('data__value', flat=True).distinct()


def line_chart(df: DataFrame, title: str, x: str, x_label: str, y: str, y_label: str) -> Dict:
    plot = figure(title=title, x_axis_label=x_label, y_axis_label=y_label, sizing_mode="stretch_both")
    plot.line(x=x, y=y, line_width=2, source=ColumnDataSource(df))
    script, div = components(plot)
    return {'script': script, 'div': div}
