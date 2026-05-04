from django.urls import path

from apps.pulls.views import PullRequestListCreateView

urlpatterns = [
    path("", PullRequestListCreateView.as_view(), name="pullrequest-list-create"),
]
