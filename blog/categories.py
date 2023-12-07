from django.db import models
from django.forms.widgets import TextInput
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, TitleFieldPanel
from wagtail.admin.widgets.slug import SlugInput
from wagtail.snippets.models import register_snippet
from wagtail.models import TranslatableMixin

@register_snippet
class BlogCategory(TranslatableMixin, models.Model):
    title = models.CharField(max_length=100, verbose_name=_("Category Name"))
    slug = models.SlugField(
        max_length=100,
        help_text=_("How the category will appear in URL"),
        # unique=True,  # <= can't use unique on translatable field
        allow_unicode=True,
    )

    panels = [
        TitleFieldPanel("title"),
        FieldPanel("slug", widget=SlugInput),
    ]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Blog Category")
        verbose_name_plural = _("Blog Categories")
        ordering = ["title"]
        unique_together = ('translation_key', 'locale'), ('locale', 'slug')
        # constraints = [
        #     models.UniqueConstraint(fields=['translation_key', 'locale'], name='unique_translation_key_locale'),
        #     models.UniqueConstraint(fields=['locale', 'slug'], name='unique_locale_slug'),
        # ]
