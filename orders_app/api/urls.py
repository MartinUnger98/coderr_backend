from django.urls import path
from .views import (
    OrderListCreateView,
    OrderStatusUpdateView,
    OrderDeleteView,
    InProgressOrderCountView,
    CompletedOrderCountView
)

urlpatterns = [
    path('orders/', OrderListCreateView.as_view()),
    path('orders/<int:pk>/', OrderStatusUpdateView.as_view()),
    path('orders/<int:pk>/delete/', OrderDeleteView.as_view()),
    path('order-count/<int:business_user_id>/',
         InProgressOrderCountView.as_view()),
    path('completed-order-count/<int:business_user_id>/',
         CompletedOrderCountView.as_view()),
]
