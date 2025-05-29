from django.urls import path
from .views import ReviewListCreateView, ReviewRetrieveUpdateDestroyView

urlpatterns = [
    path('reviews/', ReviewListCreateView.as_view()),
    path('reviews/<int:pk>/', ReviewRetrieveUpdateDestroyView.as_view()),
]
