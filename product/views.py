from django.utils.translation import gettext_lazy as _
from wagtail.admin.ui.tables import TitleColumn
from wagtail.snippets.views.chooser import (BaseSnippetChooseView,
                                            ChooseResultsView, ChooseView)

from core.viewsets.columns import ImageColumn
from core.widgets import SnippetPreviewChooserViewSet

from .models import Product


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
