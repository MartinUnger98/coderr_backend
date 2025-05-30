from rest_framework import generics, permissions, filters
from reviews_app.models import Review
from .serializers import ReviewSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from .filters import ReviewFilter
from rest_framework.response import Response
from rest_framework import status


class ReviewListCreateView(generics.ListCreateAPIView):
    """
    API view to retrieve list of reviews or create a new review.
    Only users with a customer profile can create reviews.
    One review per business user is allowed.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ['updated_at', 'rating']

    def perform_create(self, serializer):
        """
        Validates and saves a review created by a customer.
        Raises PermissionDenied if the user is not a customer
        or has already reviewed the given business user.
        """
        user = self.request.user

        if user.profile.type != 'customer':
            raise PermissionDenied("Nur Kunden dürfen Bewertungen erstellen.")

        business_user = serializer.validated_data['business_user']

        if Review.objects.filter(business_user=business_user, reviewer=user).exists():
            raise PermissionDenied(
                "Du darfst nur eine Bewertung pro Geschäftsbenutzer abgeben.")

        serializer.save(reviewer=user)


class ReviewRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update or delete a specific review.
    Only the reviewer (creator) can update or delete their review.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def check_object_permissions(self, request, obj):
        """
        Checks if the current user has permission to update or delete the review.
        Only the reviewer may perform these actions.
        """
        if request.method in ['PATCH', 'DELETE'] and obj.reviewer != request.user:
            raise PermissionDenied(
                "Nur der Ersteller darf diese Bewertung bearbeiten oder löschen.")

    def patch(self, request, *args, **kwargs):
        """
        Handles partial update of a review.
        """
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Handles deletion of a review.
        """
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
