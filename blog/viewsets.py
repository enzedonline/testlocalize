from wagtail.admin.viewsets.pages import PageListingViewSet
from wagtail.admin.ui.tables import Column

from .models import BlogPage


class BlogPageFilterSet(PageListingViewSet.filterset_class):
    class Meta:
        model = BlogPage
        fields = ["some_product"]


class BlogPageListingViewSet(PageListingViewSet):
    icon = "globe"
    menu_label = "Blog Pages"
    add_to_admin_menu = True
    model = BlogPage
    columns = PageListingViewSet.columns + [
        Column("some_product", label="Product", sort_key="some_product"),
    ]    
    filterset_class = BlogPageFilterSet

blog_page_listing_viewset = BlogPageListingViewSet("blog_pages")