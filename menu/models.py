from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import (DraftStateMixin, Locale, LockableMixin,
                            PreviewableMixin, RevisionMixin, TranslatableMixin,
                            WorkflowMixin)
from wagtail.snippets.models import register_snippet
from wagtail_localize.fields import TranslatableField, SynchronizedField
from .blocks import MenuStreamBlock
from wagtail.images.widgets import AdminImageChooser


BREAKPOINT_CHOICES = (
    # ("none", _("No breakpoint (always collapsed)")),
    # ("sm", _("Mobile screens only (<576px)")),
    ("md", _("Small Screens (<768px)")),
    ("lg", _("Medium Screens (<992px)")),
    # ("xl", _("Extra Large (<1200px)")),
)

@register_snippet
class Menu(
    TranslatableMixin,
    PreviewableMixin,
    WorkflowMixin,
    DraftStateMixin,
    LockableMixin,
    RevisionMixin,
    models.Model,
):
    title = models.CharField(max_length=255, verbose_name=_("Menu Title"))
    slug = models.SlugField()
    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
        verbose_name=_("Optional Menu Title Logo"),
    )
    items = StreamField(
        MenuStreamBlock(), verbose_name="Menu Items", blank=True, use_json_field=True
    )
    breakpoint = models.CharField(
        max_length=4,
        choices=BREAKPOINT_CHOICES,
        default="lg",
        blank=False,
        null=True,
        verbose_name=_("Mobile Layout Breakpoint"),
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("slug"),
        FieldPanel("logo", widget=AdminImageChooser(show_edit_link=False)),
        FieldPanel("breakpoint"),
        FieldPanel("items"),
    ]

    translatable_fields = [
        TranslatableField("title"),
        SynchronizedField("logo"),
        TranslatableField("items")
    ]

    def __str__(self) -> str:
        return self.title

    def get_preview_template(self, request, mode_name):
        return "menu/previews/menu.html"

    class Meta:
        verbose_name = _('Menu')
        unique_together = ('translation_key', 'locale'), ('locale', 'slug')

    def clean(self):
        # Check unique_together constraint
        # Stop instances being created outside of default locale
        # ASSUMPTION: the field in the unique_together (slug) is non-translatable

        try:
            def_lang = Locale.get_default()
        except:
            def_lang = Locale.objects.first()
        
        if self.locale==def_lang:
            # If in default locale, look for other sets with the template_set value (checking pre-save value)
            # Exclude other locales (will be translations of current locale)
            # Exclude self to cater for editing existing instance. Name change still checked against other instances.
            if Menu.objects.filter(slug=self.slug).filter(locale=self.locale_id).exclude(pk=self.pk).count()>0:
                raise ValidationError(_("This menu slug is already in use. Please only use a unique name."))
        elif self.get_translations().count()==0:
            # If not in default locale and has no translations, new instance being created outside of default, raise error
            raise ValidationError(_(f"Menus can only be created in the default language ({def_lang}). \
                                      Please create the menu in {def_lang} and use the translate option."))

    def delete(self):
        # If deleting instance in default locale, delete translations
        # Remove if clause if using multi-level translations (eg EN > ES > CA)
        try:
            def_lang = Locale.get_default()
        except:
            def_lang = Locale.objects.first()
        
        if self.locale==def_lang:
            for trans in self.get_translations():
                trans.delete()
        super().delete()
