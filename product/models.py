from django.db import models
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, path
from wagtail.fields import RichTextField
from wagtail.models import (DraftStateMixin, Locale, LockableMixin, Orderable,
                            Page, PreviewableMixin, RevisionMixin,
                            TranslatableMixin, WorkflowMixin)
from wagtail.snippets.models import register_snippet
from wagtail_localize.fields import TranslatableField

from core.translations import TranslatablePageMixin


@register_snippet
class StoreDepartment(ClusterableModel):
    code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name=_("Department Code"),
    )
    name = models.CharField(
        max_length=50,
        verbose_name=_("Name"),
    )

    panels = [
        FieldPanel("code"),
        FieldPanel("name"),
        MultiFieldPanel(
            [
                InlinePanel("department_subcategories"),
            ],
            heading=_("Department Subcategories"),
        ),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Store Department")
        verbose_name_plural = _("Store Departments")


class DepartmentSubcategory(Orderable):
    department = ParentalKey(
        "StoreDepartment",
        related_name="department_subcategories"
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name=_("Subcategory Code"),
    )
    name = models.CharField(
        max_length=50,
        verbose_name=_("Name"),
    )

    panels = [
        FieldPanel("code"),
        FieldPanel("name"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Department Subcategory")
        verbose_name_plural = _("Department Subcategories")
        constraints = [
            models.UniqueConstraint(
                fields=['department', 'name'],
                name='unique_department_departmentsubcategory_name'
            ),
        ]


class Product(
    TranslatableMixin,
    PreviewableMixin,
    WorkflowMixin,
    DraftStateMixin,
    LockableMixin,
    RevisionMixin,
    models.Model,
):
    sku = models.CharField(max_length=10, verbose_name=_("SKU"))
    title = models.CharField(max_length=100, verbose_name=_("Product Title"))
    description = RichTextField(verbose_name=_("Product Description"))
    dept_subcategory = models.ForeignKey(
        "product.DepartmentSubcategory",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
        verbose_name=_("Department Subcategory"),
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
    )
    icon = "cogs"

    panels = [
        FieldPanel("sku"),
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("image"),
    ]

    translatable_fields = [
        TranslatableField("sku"),
        TranslatableField("title"),
        TranslatableField("description"),
    ]

    def __str__(self):
        return f"{self.sku} - {self.title} ({self.locale})"
    
    @property
    def preview(self):
        return self.image or self.icon

    def get_preview_template(self, request, mode_name):
        return "products/product_detail.html"
    
    def get_department_subcategory(self):
        return f'{self.dept_subcategory.department} - {self.dept_subcategory}'

class ProductPage(TranslatablePageMixin, RoutablePageMixin, Page):
    parent_page_types = ["home.HomePage"]
    subpage_types = []
    max_count = 1

    intro = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

    @path("")
    def product_list(self, request):
        products = Product.objects.filter(locale_id=Locale.get_active().id, live=True)
        return self.render(
            request,
            context_overrides={
                "products": products,
            },
            template="product/product_list.html",
        )

    @path("<str:sku>/")
    def product_detail(self, request, sku):
        active_locale = Locale.get_active()
        # only show live products
        products = Product.objects.filter(sku=sku, live=True)
        if products and products.filter(locale_id=active_locale.id):
            # if live product in active locale
            return self.render(
                request,
                context_overrides={
                    "product": products.first().localized,
                },
                template="product/product_detail.html",
            )
        else:
            # live product not in active locale
            if products:
                # product matching sku and live in other locales, try to find product in current locale
                # redirect request to product if found and if live else send request to product list instead
                translated = products.first().get_translation_or_none(active_locale)
                return HttpResponseRedirect(self.url + (translated.sku if (translated and translated.live) else ''))
            # no live products matching that sku in this locale, redirect to product list instead
            return HttpResponseRedirect(self.url)

    @property
    def preview(self):
        if self.image:
            return self.image
