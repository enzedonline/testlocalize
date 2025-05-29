from django.utils.translation import gettext_lazy as _
from wagtail.admin.ui.tables import Column, TitleColumn, UpdatedAtColumn
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.chooser import (BaseSnippetChooseView,
                                            ChooseResultsView, ChooseView)
from wagtail.snippets.views.snippets import SnippetViewSet

from core.viewsets.columns import ImageColumn
from core.widgets import SnippetPreviewChooserViewSet

from .models import Product


class ProductViewSet(SnippetViewSet):
    model = Product
    list_display = ["title", "locale", ImageColumn("image"), "get_department_subcategory", "sku", UpdatedAtColumn()]
    list_filter = {"title": ["icontains"], "sku": ["icontains"], "dept_subcategory": ["exact"]}
    list_per_page = 50
    ordering = ["dept_subcategory", "title"]
    
setattr(Product.get_department_subcategory, 'admin_order_field', "dept_subcategory")
setattr(Product.get_department_subcategory, 'short_description', Product.dept_subcategory.field.verbose_name)
register_snippet(ProductViewSet)

class BaseProductChooseView(BaseSnippetChooseView):
    @property
    def columns(self):
        return [
            ImageColumn(
                name="image",
                label="",
                accessor="image",
                url_name=self.chosen_url_name,
                link_attrs={"data-chooser-modal-choice": True},
            ),
            TitleColumn(
                name="sku",
                label=_("SKU"),
                accessor="sku",
                url_name=self.chosen_url_name,
                link_attrs={"data-chooser-modal-choice": True},
            ),
            TitleColumn(
                name="title",
                label=_("Title"),
                accessor="title",
                url_name=self.chosen_url_name,
                link_attrs={"data-chooser-modal-choice": True},
            ),
        ]
    
    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def get_object_list(self):
        objects = super().get_object_list()
        return objects.filter(title__icontains='')  
    
class ProductChooseView(ChooseView, BaseProductChooseView):
    pass

class ProductChooseResultsView(ChooseResultsView, BaseProductChooseView):
    pass

class ProductChooserViewSet(SnippetPreviewChooserViewSet):
    model = Product
    choose_view_class = ProductChooseView
    choose_results_view_class = ProductChooseResultsView

product_chooser_viewset = ProductChooserViewSet()
