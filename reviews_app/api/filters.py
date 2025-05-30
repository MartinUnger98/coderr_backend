import django_filters
from reviews_app.models import Review


class ReviewFilter(django_filters.FilterSet):
    business_user_id = django_filters.NumberFilter(
        field_name="business_user__id")
    reviewer_id = django_filters.NumberFilter(field_name="reviewer__id")

    class Meta:
        model = Review
        fields = ['business_user_id', 'reviewer_id']
