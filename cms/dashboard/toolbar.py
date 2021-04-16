from typing import Optional

from django.utils.html import format_html
from django.utils.safestring import mark_safe


class LinkButton:
    def __init__(self, url, icon, label: Optional[str] = None, help_text: Optional[str] = None,
                 btn_class: Optional[str] = None):
        self.label = label
        self.url = url
        self.icon = icon
        self.help_text = help_text
        self.btn_class = btn_class

    def render(self):
        return format_html(
            """
            <a class="{btn_class}" href="{url}">
                <i class="{icon}"></i> {label}
            </a>
            """,
            label=self.label or '',
            url=self.url,
            icon=self.icon,
            help_text=self.help_text or '',
            btn_class=self.btn_class or ''
        )


class NavItem:
    def __init__(self, label, url, icon, active: Optional[bool] = False):
        self.label = label
        self.url = url
        self.icon = icon
        self.active = active

    def render(self):
        return format_html(
            """
            <li class="nav-item {active}">
                <a class="nav-link" href="{url}">
                    <i class="{icon}"></i>
                    <span>{label}</span></a>
            </li>
            """,
            label=self.label,
            url=self.url,
            icon=self.icon,
            active='active' if self.active else '',
        )


class DropdownItem:
    def __init__(self, dropdown_icon, dropdown_id, items, dropdown_class="", dropdown_label=""):
        self.dropdown_icon = dropdown_icon
        self.dropdown_id = dropdown_id
        self.dropdown_class = dropdown_class
        self.dropdown_label = dropdown_label
        self.items = items

    def render(self):
        items = mark_safe(u'')
        for item in self.items:
            items += self.render_item(item)
        return format_html(
            """
            <div class="dropdown no-arrow">
                <a class="dropdown-toggle {dropdown_class}" href="#" id="{dropdown_id}" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    <i class="{dropdown_icon}"></i> {dropdown_label}
                </a>
                <div class="dropdown-menu" aria-labelledby="{dropdown_id}">
                    {items}
                </div>
            </div>
            """,
            dropdown_icon=self.dropdown_icon,
            dropdown_id=self.dropdown_id,
            dropdown_label=self.dropdown_label,
            dropdown_class=self.dropdown_class,
            items=items
        )

    def render_item(self, item):
        assert isinstance(item, LinkButton), 'Items must be instances of ToolbarItem: {}'.format(item.__class__)
        return format_html(
            """
            <a class="dropdown-item" href="{url}">
                <span class="glyphicon {icon}"></span> {label}
            </a>
            """,
            url=item.url,
            icon=item.icon,
            label=item.label,
        )

