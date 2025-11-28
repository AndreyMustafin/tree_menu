from django import template
from urllib.parse import urlparse
from django.shortcuts import render
from django.db import connection
from ..models import Menu

register = template.Library()


@register.filter
def extract_menu_name(url):
    if not url:
        return ''

    if url.startswith(('http://', 'https://')):
        parsed = urlparse(url)
        path = parsed.path
        parts = path.rstrip('/').split('/')
        return parts[-1] if parts else ''

    return url


@register.inclusion_tag('menu/main_menu.html', takes_context=True)
def draw_menu(context, name=None):

    return context