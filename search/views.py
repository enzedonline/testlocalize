from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse
from wagtail.contrib.search_promotions.models import Query
from wagtail.models import Locale, Page
from wagtail.search.backends import get_search_backend

backends = list(settings.WAGTAILSEARCH_BACKENDS.keys())

def search(request):
    search_query = request.GET.get("query", None)
    page = request.GET.get("page", 1)

    # Search
    if search_query:
        locale=Locale.get_active()
        scope = Page.objects.live().defer_streamfields().filter(locale=locale)
        backend = get_search_backend(locale.language_code if locale.language_code in backends else 'default')
        search_results = backend.search(search_query, scope)

        # Record hit
        query = Query.get(search_query)
        query.add_hit()
    else:
        search_results = Page.objects.none()

    # Pagination
    paginator = Paginator(search_results, 10)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return TemplateResponse(
        request,
        "search/search.html",
        {
            "search_query": search_query,
            "search_results": search_results,
        },
    )
