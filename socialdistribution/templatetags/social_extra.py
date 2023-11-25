import markdown

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()
# https://www.youtube.com/watch?v=t61nTi0lIlk
# https://stackoverflow.com/questions/48842889/django-templatesyntaxerror-invalid-filter/65363914#65363914
@register.filter
@stringfilter
def convert_markdown(value):
    return markdown.markdown(value,extension_configs=['markdown.extensions.fense_code'])