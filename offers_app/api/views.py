from rest_framework import generics, status, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Offer, OfferDetail
from .serializers import (
    OfferListSerializer,
    OfferCreateUpdateSerializer,
    OfferDetailSerializer,
    FileUploadSerializer
)
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .pagination import LargeResultsSetPagination
from .filters import OfferFilter
from django.db.models import Min


class OfferListCreateView(generics.ListCreateAPIView):
    """
    API view to list all offers or create a new offer.
    Offers can be filtered, searched, and ordered.
    Only authenticated users with a 'business' profile can create offers.
    """
    queryset = Offer.objects.all().prefetch_related('details', 'user')
    filter_backends = [DjangoFilterBackend,
                       filters.OrderingFilter, filters.SearchFilter]
    filterset_class = OfferFilter
    ordering_fields = ['updated_at', 'min_price']
    search_fields = ['title', 'description']
    pagination_class = LargeResultsSetPagination

    def get_serializer_class(self):
        """
        Return the serializer class depending on the request method.
        """
        if self.request.method == 'POST':
            return OfferCreateUpdateSerializer
        return OfferListSerializer

    def get_queryset(self):
        """
        Return annotated and filtered queryset based on query params.
        """
        queryset = self._annotate_queryset(Offer.objects.all())
        return self._apply_filters(queryset)

    def _annotate_queryset(self, queryset):
        """
        Annotate offers with minimum price and delivery time values.
        """
        return queryset.annotate(
            min_price=Min('details__price'),
            min_delivery_time=Min('details__delivery_time_in_days')
        ).prefetch_related('details', 'user')

    def _apply_filters(self, queryset):
        """
        Apply optional filters for minimum price and maximum delivery time.
        """
        min_price = self.request.query_params.get('min_price')
        max_delivery = self.request.query_params.get('max_delivery_time')

        if min_price:
            queryset = queryset.filter(min_price__gte=min_price)
        if max_delivery:
            queryset = queryset.filter(min_delivery_time__lte=max_delivery)

        return queryset

    def perform_create(self, serializer):
        """
        Validate user and save new offer with authenticated business user.
        """
        user = self.request.user
        if not user.is_authenticated:
            raise AuthenticationFailed("Benutzer ist nicht authentifiziert.")
        if user.profile.type != 'business':
            raise PermissionDenied(
                "Nur Benutzer mit einem 'business'-Profil dürfen Angebote erstellen.")
        serializer.save(user=user)


class OfferRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a single offer.
    Only the offer creator can update or delete the offer.
    """
    queryset = Offer.objects.all().prefetch_related('details', 'user')
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """
        Return the serializer class depending on the request method.
        """
        if self.request.method in ['PATCH', 'PUT']:
            return OfferCreateUpdateSerializer
        return OfferListSerializer

    def check_object_permissions(self, request, obj):
        """
        Restrict modification/deletion to the offer creator only.
        """
        if request.method in ['PATCH', 'DELETE']:
            if obj.user != request.user:
                raise PermissionDenied(
                    "Nur der Ersteller darf dieses Angebot ändern oder löschen.")

    def delete(self, request, *args, **kwargs):
        """
        Handle deletion of an offer after permission check.
        """
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class OfferDetails(generics.RetrieveAPIView):
    """
    API view to retrieve the details of a specific OfferDetail.
    Only accessible to authenticated users.
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]


class FileUploadView(APIView):
    """
    API view to upload files for the authenticated user's offer.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        """
        Handle file upload and attach it to the user's offer.
        """
        offer = Offer.objects.get(user=request.user)
        serializer = FileUploadSerializer(
            offer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
