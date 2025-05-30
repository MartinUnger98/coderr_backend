import django_filters
from reviews_app.models import Review


class ReviewFilter(django_filters.FilterSet):
    """
    FilterSet for filtering reviews by business user or reviewer.

    Allows filtering reviews using:
    - business_user_id: ID of the business user who received the review
    - reviewer_id: ID of the user who wrote the review
    """
    business_user_id = django_filters.NumberFilter(
        field_name="business_user__id"
    )
    reviewer_id = django_filters.NumberFilter(field_name="reviewer__id")

    class Meta:
        model = Review
        fields = ['business_user_id', 'reviewer_id']
