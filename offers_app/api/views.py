from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Offer, OfferDetail
from .serializers import (
    OfferListSerializer,
    OfferCreateUpdateSerializer,
    OfferDetailSerializer,
    FileUploadSerializer
)
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .pagination import LargeResultsSetPagination


class OfferListCreateView(generics.ListCreateAPIView):
    queryset = Offer.objects.all().prefetch_related('details', 'user')
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['user__id']
    ordering_fields = ['updated_at', 'details__price']
    search_fields = ['title', 'description']
    pagination_class = LargeResultsSetPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OfferCreateUpdateSerializer
        return OfferListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        min_price = self.request.query_params.get('min_price')
        max_delivery = self.request.query_params.get('max_delivery_time')

        if min_price:
            queryset = queryset.filter(details__price__gte=min_price)
        if max_delivery:
            queryset = queryset.filter(details__delivery_time_in_days__lte=max_delivery)

        return queryset.distinct()

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_authenticated:
            raise PermissionDenied("Benutzer ist nicht authentifiziert.")
        if user.profile.type != 'business':
            raise PermissionDenied("Nur Benutzer mit einem 'business'-Profil dürfen Angebote erstellen.")
        serializer.save(user=user)


class OfferRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.all().prefetch_related('details', 'user')
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return OfferCreateUpdateSerializer
        return OfferListSerializer

    def check_object_permissions(self, request, obj):
        if request.method in ['PATCH', 'DELETE']:
            if obj.user != request.user:
                raise PermissionDenied("Nur der Ersteller darf dieses Angebot ändern oder löschen.")

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    lookup_field = 'id'
    permission_classes = [permissions.AllowAny]
    
class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        offer = Offer.objects.get(user=request.user)
        serializer = FileUploadSerializer(offer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
