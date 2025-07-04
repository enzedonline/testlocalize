import logging
from django import template
from django.utils.translation import get_language
from wagtail.models import Locale

register = template.Library()

@register.simple_tag(takes_context=True)
def translated_text(context, field_name='text'):
    try:
        request = context.get("request")
        items = context.get('self').bound_blocks
        current_lang = getattr(request, "LANGUAGE_CODE", None) or get_language()
        # Try exact match
        match = next(
            (item for item in items if item.value.get("language", "") == current_lang),
            None
        )
        # If not found, try base language (e.g. "es" from "es-mx") if locale includes region
        if not match and "-" in current_lang:
            base_lang = current_lang.split("-")[0]
            match = next(
                (item for item in items if item.value.get("language", "") == base_lang),
                None
            )
        # If still not found, try default locale
        if not match:
            default_lang = Locale.get_default().language_code
            match = next(
                (item for item in items if item.value.get("language", "") == default_lang),
                None
            )
        return match.value.get(field_name, "") if match else ""
    except Exception as e:
        logging.error(
            f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}"
        )
    return ""