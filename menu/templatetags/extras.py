from django import template
from urllib.parse import urlparse

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