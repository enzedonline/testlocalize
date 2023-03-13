from django.db import models
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, path
from wagtail.fields import RichTextField
from wagtail.models import Locale, Page, TranslatableMixin
from wagtail.snippets.models import register_snippet
from wagtail_localize.fields import TranslatableField


@register_snippet
class Product(TranslatableMixin, models.Model):
    sku = models.CharField(max_length=10, verbose_name=_("SKU"))
    title = models.CharField(max_length=100, verbose_name=_("Product Title"))
    description = models.TextField(verbose_name=_("Product Description"))

    panels = [
        FieldPanel('sku'),
        FieldPanel('title'),
        FieldPanel('description')
    ]

    translatable_fields = [
        TranslatableField("title"),
        TranslatableField("description"),
    ]

    def __str__(self):
        return f'{self.sku} - {self.title}'

class ProductPage(RoutablePageMixin, Page):
    intro = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

    @path('')
    def product_list(self, request):
        products = Product.objects.filter(locale_id=Locale.get_active().id)
        return self.render(
            request,
            context_overrides={
                'products': products,
            },
            template="products/product_list.html",
        )

    @path('<str:sku>/')
    def product_detail(self, request, sku):
        product = Product.objects.filter(sku=sku).first()
        if product:
            return self.render(
                request,
                context_overrides={
                    'product': product.localized,
                },
                template="products/product_detail.html",
            )
        else:
            return HttpResponseRedirect(self.url)