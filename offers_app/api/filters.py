from django_filters import rest_framework as filters
from offers_app.models import Offer


class OfferFilter(filters.FilterSet):
    """
    FilterSet for filtering Offer instances based on query parameters.

    This filter allows filtering offers by the ID of the user who created them.
    """
    creator_id = filters.NumberFilter(field_name='user__id')

    class Meta:
        model = Offer
        fields = ['creator_id']
