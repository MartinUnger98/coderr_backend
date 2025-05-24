from django.urls import path
from .views import (
    OfferListCreateView,
    OfferRetrieveUpdateDestroyView,
    OfferDetailRetrieveView,
    FileUploadView
)

urlpatterns = [
    path('offers/', OfferListCreateView.as_view(), name='offer-list-create'),
    path('offers/<int:id>/', OfferRetrieveUpdateDestroyView.as_view(), name='offer-detail-update-delete'),
    path('offerdetails/<int:id>/', OfferDetailRetrieveView.as_view(), name='offerdetail-retrieve'),
    path('upload/', FileUploadView.as_view(), name='file-upload'),
]
