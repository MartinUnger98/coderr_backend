from django.urls import path
from .views import RegistrationView, CustomLoginView, UserProfileDetailView, BusinessProfileListView, CustomerProfileListView, FileUploadView

urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("profile/<int:pk>/", UserProfileDetailView.as_view(), name="profile-detail"),
    path("profiles/business/", BusinessProfileListView.as_view(),
         name="business-profiles"),
    path("profiles/customer/", CustomerProfileListView.as_view(),
         name="customer-profiles"),
    path('upload/', FileUploadView.as_view(), name='file-upload'),
]
