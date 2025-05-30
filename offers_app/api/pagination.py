from rest_framework.pagination import PageNumberPagination


class LargeResultsSetPagination(PageNumberPagination):
    """
    Custom pagination class for handling large sets of results.

    Defaults to 6 items per page, but allows clients to control the page size
    via the 'page_size' query parameter, up to a maximum of 100 items.
    """
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100
