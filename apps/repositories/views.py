from rest_framework import generics

from apps.repositories.models import Repository
from apps.repositories.serializers import RepositorySerializer


class RepositoryListCreateView(generics.ListCreateAPIView):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer
