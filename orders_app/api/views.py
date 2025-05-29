from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import Order
from .serializers import OrderSerializer
from offers_app.models import OfferDetail
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.models import User

class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(Q(customer_user=user) | Q(business_user=user))

    def create(self, request, *args, **kwargs):
        user = self.request.user
        if user.profile.type != 'customer':
            return Response({'detail': 'Nur Kunden dürfen Bestellungen erstellen.'}, status=403)
        
        offer_detail_id = request.data.get('offer_detail_id')
        if not offer_detail_id:
            return Response({'detail': 'offer_detail_id fehlt.'}, status=400)

        offer_detail = get_object_or_404(OfferDetail, id=offer_detail_id)
        order = Order.objects.create(
            customer_user=user,
            business_user=offer_detail.offer.user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type
        )
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=201)

class OrderStatusUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user
        if user.profile.type != 'business':
            return Response({'detail': 'Nur Geschäftsnutzer dürfen den Status ändern.'}, status=403)
        
        status_value = request.data.get('status')
        if status_value not in dict(Order.STATUS_CHOICES):
            return Response({'detail': 'Ungültiger Status.'}, status=400)

        instance.status = status_value
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class OrderDeleteView(generics.DestroyAPIView):
    queryset = Order.objects.all()
    permission_classes = [IsAdminUser]

class InProgressOrderCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        get_object_or_404(User, id=business_user_id, profile__type='business')
        count = Order.objects.filter(business_user_id=business_user_id, status='in_progress').count()
        return Response({'order_count': count})

class CompletedOrderCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        get_object_or_404(User, id=business_user_id, profile__type='business')
        count = Order.objects.filter(business_user_id=business_user_id, status='completed').count()
        return Response({'completed_order_count': count})
