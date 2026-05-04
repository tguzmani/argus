from django.urls import path

from apps.repositories.views import RepositoryListCreateView

urlpatterns = [
    path("", RepositoryListCreateView.as_view(), name="repository-list-create"),
]
