from django_filters import rest_framework as filters
from offers_app.models import Offer

class OfferFilter(filters.FilterSet):
    creator_id = filters.NumberFilter(field_name='user__id')

    class Meta:
        model = Offer
        fields = ['creator_id']
