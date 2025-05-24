from django.urls import path
from .views import (
    OfferListCreateView,
    OfferRetrieveUpdateDestroyView,
    OfferDetails,
    FileUploadView
)

urlpatterns = [
    path('offers/', OfferListCreateView.as_view(), name='offer-list-create'),
    path('offers/<int:id>/', OfferRetrieveUpdateDestroyView.as_view(), name='offer-detail-update-delete'),
    path('offerdetails/<int:id>/', OfferDetails.as_view(), name='offer-details'),
    path('upload/', FileUploadView.as_view(), name='file-upload'),
]
