from wagtail import hooks
from .views import SVGIconChooserViewSet
from wagtail.snippets.models import register_snippet
from .models import SVGIcon
from .views import SVGViewSet
from django.templatetags.static import static
from django.utils.safestring import mark_safe

@hooks.register('register_admin_viewset')
def register_svg_icon_chooser_viewset():
    return SVGIconChooserViewSet('svg_icon_chooser', url_prefix='svg-icon-chooser')

register_snippet(SVGIcon, viewset=SVGViewSet)

@hooks.register('insert_editor_css')
def svg_editor_css():
    chooser_css = static('css/svg-chooser.css')
    field_panel_css = static('css/svg-field-panel.css')
    viewset_css = static('css/svg-viewset.css')
    return mark_safe(
        f'<link rel="stylesheet" href="{chooser_css}">\
          <link rel="stylesheet" href="{field_panel_css}">\
          <link rel="stylesheet" href="{viewset_css}">'
    )

@hooks.register('insert_editor_js')
def svg_editor_js():
    field_panel_js = static('js/svg-panel-preview.js')
    return mark_safe(
        f'<script src="{field_panel_js}"></script>'
    )
