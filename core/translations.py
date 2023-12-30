from django.conf import settings
from django.utils.functional import cached_property
from wagtail.models import Locale


class ExtendedTranslatableMixin:
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
            x_default = list(self.translations.items())[0][1]
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
