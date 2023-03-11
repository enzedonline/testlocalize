from django.core.exceptions import ValidationError
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Locale, TranslatableMixin
from wagtail.snippets.models import register_snippet

from svg.chooser.widget import SVGChooser

from .blocks import MenuStreamBlock


@register_snippet
class Menu(TranslatableMixin, models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Menu Title"))
    slug = models.SlugField()
    icon = models.ForeignKey(
        'svg.SVGIcon',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+', 
        verbose_name=_("Optional Menu Title Logo")
    )
    items = StreamField(
        MenuStreamBlock(), verbose_name="Menu Items", blank=True, use_json_field=True
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('slug'),
        FieldPanel('icon', widget=SVGChooser),
        FieldPanel('items')
    ]

    def __str__(self) -> str:
        return self.title

    @property
    def logo(self):
        return mark_safe(self.icon.svg) if self.icon else ''
    
    class Meta:
        verbose_name = _('Menu')
        unique_together = ('translation_key', 'locale'), ('locale', 'slug')

    def clean(self):
        # Check unique_together constraint
        # Stop instances being created outside of default locale
        # ASSUMPTION: the field in the unique_together (template_set) is non-translatable

        def_lang = Locale.get_default()
        
        if self.locale==Locale.get_default():
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
        if self.locale==Locale.get_default():
            for trans in self.get_translations():
                trans.delete()
        super().delete()

