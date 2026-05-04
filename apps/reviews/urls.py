from django.urls import path

from apps.reviews.views import (
    ReviewSessionApproveView,
    ReviewSessionDetailView,
    ReviewSessionListCreateView,
    ReviewSessionRejectView,
)

urlpatterns = [
    path("", ReviewSessionListCreateView.as_view(), name="reviewsession-list-create"),
    path("<int:pk>/", ReviewSessionDetailView.as_view(), name="reviewsession-detail"),
    path("<int:pk>/approve/", ReviewSessionApproveView.as_view(), name="reviewsession-approve"),
    path("<int:pk>/reject/", ReviewSessionRejectView.as_view(), name="reviewsession-reject"),
]
