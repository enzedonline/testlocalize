from django.conf import settings
from django.utils.functional import cached_property
from wagtail.models import Locale
from wagtail_localize.models import Translation, TranslationSource


def get_translation_predecessor(item):
    """ 
    Return object an item was directly translated from. Returns None if not translated or is original (source text).
    """
    try:
        translation_match = (
            Translation.objects
            .select_related('source') 
            .get(source__object_id=item.translation_key, target_locale_id=item.locale.id)
        )
        return item.get_translation(translation_match.source.locale)
    except Translation.DoesNotExist:
        return None
    
def get_translation_source(item):
    """ 
    Return the original (source) object an item was translated from.
    """
    source = get_translation_predecessor(item)
    if source:
        return get_translation_source(source)
    else:
        return item

def get_translated_items(item):
    """
    Recursively find all translated items with this instance as source (either directly or indirectly)
    """
    translated_items = item.direct_translations
    for translation in translated_items:
        translated_items.extend(get_translated_items(translation))
    return translated_items

class ExtendedTranslatableMixin:
    @cached_property
    def translation_predecessor(self):
        """ 
        Return object an item was directly translated from. Returns self if not translated or is origin.
        """
        result = get_translation_predecessor(self)
        return result or self
    
    @cached_property
    def translation_source(self):
        """ 
        Return the source (origin) object this instance translated from. Returns self if not translated or is origin.
        """
        if self.translation_predecessor == self:
            return self
        else:
            return get_translation_source(self.translation_predecessor)

    @property
    def direct_translations(self):
        """
        Return all items that have been directly translated from the given source item.
        This only includes translations with the same translation_key that use item as their source.
        """
        # Retrieve the translation source object for the item
        try:
            source = TranslationSource.objects.get(object_id=self.translation_key, locale_id=self.locale.id)
        except TranslationSource.DoesNotExist:
            return []  # No descendants if item has no translation source

        # Find all translations linked to this source
        translations = (
            Translation.objects
            .filter(source=source)
            .select_related('target_locale')
        )

        # Retrieve each translated item in the target locales
        return [
            self.get_translation(translation.target_locale)
            for translation in translations
        ]
        
    
    @property
    def translated_items(self):
        """
        Recursively find all translated items with this instance as source (either directly or indirectly)
        """
        return get_translated_items(self)

                

    @property
    def localized_or_none(self):
        """
        Amends the default Wagtail localized property to return None if the page/model is
        either not translated or translation is not live.
        """
        from wagtail.models import DraftStateMixin

        localized = self.localized_draft_or_none
        if localized and isinstance(self, DraftStateMixin) and not localized.live:
            return None

        return localized

    @property
    def localized_draft_or_none(self):
        """
        Amends the default Wagtail localized_draft property to return None if the page/model is
        not translated.
        """
        if not getattr(settings, "WAGTAIL_I18N_ENABLED", False):
            return self

        try:
            locale = Locale.get_active()
        except (LookupError, Locale.DoesNotExist):
            return self

        if locale.id == self.locale_id:
            return self

        return self.get_translation_or_none(locale)


class TranslatablePageMixin(ExtendedTranslatableMixin):
    @property
    def search_engine_index(self):
        return True

    @cached_property
    def translations(self):
        """
        Return dict of lang-code/url key/value pairs for each page that has a live translation including self
        Urls are relative.
        """
        return {
            page.locale.language_code: page.url
            for page in self.get_translations(inclusive=True)
            .live()
            .defer_streamfields()
        }

    @cached_property
    def alternates(self):
        """
        Create list of translations for <link rel="alternate" ...> head entries.
        Convert translations dict into list of dictionaries with lang_code and location keys for each translations item.
        Convert translations urls to absolute urls instead of relative urls
        Add x-default value.
        """
        site_root = self.get_site().root_url
        alt = [
            {"lang_code": key, "location": f"{site_root}{value}"}
            for key, value in self.translations.items()
        ]
        x_default = self.translations.get(Locale.get_default().language_code)
        if not x_default:
            # doesn't exist in default locale, use the first locale in the translations
            try:
                x_default = list(self.translations.items())[0][1]
            except:
                x_default = self.url
        alt.append({"lang_code": "x-default", "location": f"{site_root}{x_default}"})
        return alt

    def get_sitemap_urls(self):
        """
        Return sitemap entry for this page including alternates values
        """
        url_item = {
            "location": self.full_url,
            "lastmod": self.last_published_at or self.latest_revision_created_at,
            "alternates": self.alternates,
        }
        # if self.search_engine_changefreq:
        #     url_item["changefreq"] = self.search_engine_changefreq
        # if self.search_engine_priority:
        #     url_item["priority"] = self.search_engine_priority

        return url_item
