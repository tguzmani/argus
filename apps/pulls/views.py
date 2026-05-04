from rest_framework import generics

from apps.pulls.models import PullRequest
from apps.pulls.serializers import PullRequestSerializer


class PullRequestListCreateView(generics.ListCreateAPIView):
    queryset = PullRequest.objects.all()
    serializer_class = PullRequestSerializer
