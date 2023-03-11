from django.utils.translation import gettext_lazy as _
from generic_chooser.views import ModelChooserMixin, ModelChooserViewSet
from wagtail.admin.ui.tables import UpdatedAtColumn
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import SVGFilterSet, SVGIcon


class SVGViewSet(SnippetViewSet):
    list_display = ["icon", "label", UpdatedAtColumn()]
    filterset_class = SVGFilterSet

class SVGIconChooserMixin(ModelChooserMixin):
    results_template = 'widgets/svg_chooser_results.html'

    @property
    def is_searchable(self):
        return True
    
    def get_row_data(self, item):
        return {
            'object_id': self.get_object_id(item),
            'choose_url': self.get_chosen_url(item),
            'title': self.get_object_string(item),
            'icon': getattr(item, 'svg', ''),
        }

    def get_chosen_response_data(self, item):
        return {
            'id': str(self.get_object_id(item)),
            'string': self.get_object_string(item),
            'icon': getattr(item, 'svg', ''),
            'edit_link': self.get_edit_item_url(item)
        }

    def get_object_list(self, search_term=None, **kwargs):
        object_list = self.get_unfiltered_object_list()
        if search_term:
            object_list = object_list.filter(label__icontains=search_term)
        return object_list

class SVGIconChooserViewSet(ModelChooserViewSet):
    icon = 'image'
    model = SVGIcon
    page_title = _("Choose an icon")
    per_page = 18
    order_by = 'label'
    chooser_mixin_class = SVGIconChooserMixin
    form_fields = None
