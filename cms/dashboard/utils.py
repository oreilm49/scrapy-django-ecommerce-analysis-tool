from statistics import mean
from typing import List, Optional, Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from cms.models import Product

from bokeh.embed import components
from bokeh.plotting import figure, ColumnDataSource
from pandas import DataFrame


def line_chart(df: DataFrame, title: str, x: str, x_label: str, y: str, y_label: str) -> Optional[Dict]:
    if df.empty:
        return None
    plot = figure(title=title, x_axis_label=x_label, y_axis_label=y_label, sizing_mode="stretch_both")
    plot.line(x=x, y=y, line_width=2, source=ColumnDataSource(df))
    script, div = components(plot)
    return {'script': script, 'div': div}


def average_price_gap(products: List['Product']):
    price_gaps = []
    for index, product in enumerate(products, start=1):
        if index < len(products):
            price_gaps.append(products[index].current_average_price_int - product.current_average_price_int)
    return mean(price_gaps)
