from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import Order
from .serializers import OrderSerializer
from offers_app.models import OfferDetail
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError


class OrderListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating orders.
    Customers can create new orders from an offer detail.
    Lists all orders where the user is either customer or business user.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns all orders related to the logged-in user.
        """
        user = self.request.user
        return Order.objects.filter(Q(customer_user=user) | Q(business_user=user))

    def create(self, request, *args, **kwargs):
        """
        Creates an order if the user is a customer and provides a valid offer_detail_id.
        """
        user = request.user
        if not self._is_customer(user):
            return Response({'detail': 'Nur Kunden dürfen Bestellungen erstellen.'}, status=403)

        offer_detail = self._get_offer_detail_or_error(request)
        order = self._create_order_from_offer(user, offer_detail)

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _is_customer(self, user):
        """
        Checks if the user is a customer.
        """
        return user.profile.type == 'customer'

    def _get_offer_detail_or_error(self, request):
        """
        Retrieves and validates the provided offer_detail_id.
        """
        offer_detail_id = request.data.get('offer_detail_id')
        if not offer_detail_id:
            raise ValidationError({'detail': 'offer_detail_id fehlt.'})
        return get_object_or_404(OfferDetail, id=offer_detail_id)

    def _create_order_from_offer(self, user, offer_detail):
        """
        Creates an Order instance based on the selected offer detail.
        """
        return Order.objects.create(
            customer_user=user,
            business_user=offer_detail.offer.user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type
        )


class OrderStatusUpdateView(generics.UpdateAPIView):
    """
    API view to allow business users to update the status of an order.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def partial_update(self, request, *args, **kwargs):
        """
        Updates the order status if the user is a business user.
        """
        instance = self.get_object()
        user = self.request.user
        if user.profile.type != 'business':
            return Response({'detail': 'Nur Geschäftsnutzer dürfen den Status ändern.'}, status=status.HTTP_403_FORBIDDEN)

        status_value = request.data.get('status')
        if status_value not in dict(Order.STATUS_CHOICES):
            return Response({'detail': 'Ungültiger Status.'}, status=status.HTTP_400_BAD_REQUEST)

        instance.status = status_value
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class OrderDeleteView(generics.DestroyAPIView):
    """
    API view that allows admin users to delete orders.
    """
    queryset = Order.objects.all()
    permission_classes = [IsAdminUser]


class InProgressOrderCountView(APIView):
    """
    API view to return the count of 'in_progress' orders for a business user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """
        Returns the number of in-progress orders for the given business user ID.
        """
        get_object_or_404(User, id=business_user_id, profile__type='business')
        count = Order.objects.filter(
            business_user_id=business_user_id, status='in_progress').count()
        return Response({'order_count': count})


class CompletedOrderCountView(APIView):
    """
    API view to return the count of 'completed' orders for a business user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """
        Returns the number of completed orders for the given business user ID.
        """
        get_object_or_404(User, id=business_user_id, profile__type='business')
        count = Order.objects.filter(
            business_user_id=business_user_id, status='completed').count()
        return Response({'completed_order_count': count})
