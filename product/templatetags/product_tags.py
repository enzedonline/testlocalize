from django import template
from wagtail.models import Locale

register = template.Library()

@register.simple_tag(takes_context=True)
def get_alternates(context):
    page = context.get('page')
    product = context.get('product')

    alternates = []
    active_locale = Locale.get_active()

    for locale in Locale.objects.all():
        if locale != active_locale:
            trans_page = page.get_translation(locale)
            subpage = trans_page.reverse_subpage('product_detail', kwargs={'sku': product.sku})
            alternates.append({'lang': locale.language_code, 'href': f'{trans_page.url}{subpage}'})
    
    return alternates
