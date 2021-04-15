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

