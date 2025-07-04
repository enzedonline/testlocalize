from django.conf import settings
from django.forms import Media, ValidationError
from django.forms.utils import ErrorList
from django.utils.functional import cached_property, lazy
from django.utils.translation import gettext_lazy as _
from wagtail.blocks import (CharBlock, ChoiceBlock, ListBlock,
                            ListBlockValidationError, StructBlock)
from wagtail.blocks.struct_block import StructBlockAdapter
from wagtail.models import Locale
from wagtail.telepath import register

get_default_language_code = lazy(lambda: Locale.get_default().language_code, str)


class TranslatableTextBlock(StructBlock):
    def __init__(self, default_text: str = None, default_language: str = None, local_blocks=None, search_index=True, **kwargs):
        local_blocks = [
            (
                "language",
                ChoiceBlock(
                    choices=settings.LANGUAGES,
                    default=default_language or get_default_language_code,
                    help_text=_("Select the language for this text")
                )
            ),
            (
                "text",
                CharBlock(
                    default=default_text or None,
                    help_text=_("Enter your text in the selected language"),
                )
            )
        ]
        super().__init__(local_blocks, search_index, **kwargs)

    class Meta:
        form_classname = "struct-block translatable-text-block"
        # form_template = 'blocks/translatable_text_block_admin.html'
        icon = 'doc-full'
        label = _('Translated text')


# class TranslatableTextBlockAdapter(StructBlockAdapter):
#     js_constructor = "website.blocks.TranslatableTextBlock"

#     @cached_property
#     def media(self):
#         structblock_media = super().media
#         return Media(
#             js=structblock_media._js + ["js/translatable_text_block.js"],
#             css=structblock_media._css
#         )


# register(TranslatableTextBlockAdapter(), TranslatableTextBlock)


class TranslatableTextListBlock(ListBlock):
    def __init__(self, **kwargs):
        super().__init__(TranslatableTextBlock(), **kwargs)

    def clean(self, value):
        cleaned_value = super().clean(value)  

        default_locale = Locale.get_default()
        seen_langs = set()
        has_default = False
        block_errors = {}
        non_block_errors = ErrorList()

        for index, item in enumerate(cleaned_value):
            lang = item.get('language')

            if lang in seen_langs:
                block_errors[index] = ValidationError({
                    'language': [_("A text for this language has already been defined.")]
                })
            else:
                seen_langs.add(lang)

            if lang == default_locale.language_code:
                has_default = True

        if not has_default:
            non_block_errors.append(
                ValidationError(f"{_('At least one item must use the default site language')} {default_locale.language_name}.")
            )

        if block_errors or non_block_errors:
            raise ListBlockValidationError(
                block_errors=block_errors,
                non_block_errors=non_block_errors
            )

        return cleaned_value

    class Meta:
        template = 'blocks/translatable_text_block.html'
