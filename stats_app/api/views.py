from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from reviews_app.models import Review
from offers_app.models import Offer
from users_app.models import UserProfile
from django.db.models import Avg


class BaseInfoView(APIView):
    """
    API view to retrieve basic platform statistics.

    Returns the total number of reviews, the average review rating,
    the total number of business profiles, and the total number of offers.
    """

    def get(self, request):
        """
        Handle GET request to return summary statistics.

        Returns:
            Response: A JSON response containing counts and averages.
        """
        review_count = Review.objects.count()
        average_rating = Review.objects.aggregate(
            avg_rating=Avg('rating'))['avg_rating'] or 0
        average_rating = round(average_rating, 1)
        business_profile_count = UserProfile.objects.filter(
            type='business').count()
        offer_count = Offer.objects.count()

        data = {
            "review_count": review_count,
            "average_rating": average_rating,
            "business_profile_count": business_profile_count,
            "offer_count": offer_count
        }
        return Response(data, status=status.HTTP_200_OK)
