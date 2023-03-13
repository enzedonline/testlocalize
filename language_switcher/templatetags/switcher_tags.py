from django import template
from wagtail.models import Locale

register = template.Library()


@register.simple_tag(takes_context=True)
def language_switcher(context, page):
    # Build the language switcher
    # determine next_url for each locale if page has translation
    # /lang/<lang-code> redirects to menu.views.set_language_from_url:
    #     path('lang/<str:language_code>/', set_language_from_url),
    # if no ?next= param passed to the view, it will attempt to determine best url from HTTP_REFERER
    # this will happen if non-Wagtail page is served, or if Wagtail page has no translation

    current_lang = Locale.get_active()
    switcher = {'alternatives': []}

    for locale in Locale.objects.all():

        if locale == current_lang: 
            switcher['current'] = locale
        else: # add the link to switch language 
            next_url = ''
            try:
                # if page has live translation forward to that page, else forward to home page in new locale
                trans_page = page.get_translation_or_none(locale=locale)
                if trans_page and trans_page.live:
                    try: 
                        # if routable page, construct translated routable url
                        # the kwargs will be untranslated, you will need to handle the localization in the 
                        #   path definition in your routable page model
                        resolver = page.get_resolver().resolve(context.request.path.replace(page.url, '/'))
                        subpage = trans_page.reverse_subpage(resolver.view_name, kwargs=resolver.kwargs)
                        next_url = f'?next={trans_page.url}{subpage}'
                    except:
                        next_url = f'?next={trans_page.url}'
                else:
                    next_url = f'?next=/{locale.language_code}/'
            except AttributeError: # non-Wagtail page, let view determine best url to forward to
                next_url = ''
            switcher['alternatives'].append(
                {
                    'name': locale.get_display_name(), 
                    'language_code': locale.language_code,
                    'url': f'/lang/{locale.language_code}/{next_url}'
                }
            )

    return switcher

