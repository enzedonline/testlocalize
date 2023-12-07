from django import template
from wagtail.models import Locale
from wagtail.contrib.routable_page.models import RoutablePageMixin

register = template.Library()

def get_routable_subpage_url(page, context):
    # if routable page, construct translated routable url
    # the kwargs will be untranslated, you will need to handle the localization in the 
    #   path definition in your routable page model
    request = context.get('request', False)
    if request:
        resolver = page.get_resolver().resolve(request.path.replace(page.url, '/'))
        return page.reverse_subpage(resolver.view_name, kwargs=resolver.kwargs)
    else:
        return ''

@register.simple_tag(takes_context=True)
def language_switcher(context):
    # Build the language switcher
    # determine next_url for each locale if page has translation
    # /lang/<lang-code> redirects to menu.views.set_language_from_url:
    #     path('lang/<str:language_code>/', set_language_from_url),
    # if no ?next= param passed to the view, it will attempt to determine best url from HTTP_REFERER
    # this will happen if non-Wagtail page is served, or if Wagtail page has no translation

    current_lang = Locale.get_active()
    switcher = {'alternatives': []}

    page = context.get('page', False)
    if page:
        for locale in Locale.objects.all():
            if locale == current_lang: 
                switcher['current'] = locale
            else: # add the link to switch language 
                next_url = page.translations.get(locale.language_code, '')
                if next_url:
                    if isinstance(page, RoutablePageMixin):
                        next_url += context['request'].path.replace(page.url, '')
                    next_url = f'?next={next_url}'
                    
                switcher['alternatives'].append(
                    {
                        'name': locale.get_display_name(), 
                        'code': locale.language_code,
                        'url': f'/lang/{locale.language_code}/{next_url}'
                    }
                )
    else:
        for locale in Locale.objects.all():            
            if locale == current_lang: 
                switcher['current'] = locale
            else:
                switcher['alternatives'].append(
                    {
                        'name': locale.get_display_name(), 
                        'code': locale.language_code,
                        'url': f'/lang/{locale.language_code}/'
                    }
            )
    return switcher

