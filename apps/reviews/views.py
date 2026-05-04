from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.reviews.models import ReviewSession
from apps.reviews.serializers import (
    ReviewSessionDetailSerializer,
    ReviewSessionSerializer,
)


class ReviewSessionListCreateView(generics.ListCreateAPIView):
    queryset = ReviewSession.objects.all()
    serializer_class = ReviewSessionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = serializer.save()
        return Response(
            {"id": session.id, "thread_id": str(session.thread_id), "status": session.status},
            status=status.HTTP_201_CREATED,
        )


class ReviewSessionDetailView(generics.RetrieveAPIView):
    queryset = ReviewSession.objects.prefetch_related("findings")
    serializer_class = ReviewSessionDetailSerializer


class ReviewSessionApproveView(APIView):
    def post(self, request, pk):
        try:
            session = ReviewSession.objects.get(pk=pk)
        except ReviewSession.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if session.status != ReviewSession.Status.AWAITING_APPROVAL:
            return Response(
                {"detail": f"Cannot approve session with status '{session.status}'."},
                status=status.HTTP_409_CONFLICT,
            )

        session.status = ReviewSession.Status.APPROVED
        session.save(update_fields=["status", "updated_at"])
        return Response({"id": session.id, "status": session.status})


class ReviewSessionRejectView(APIView):
    def post(self, request, pk):
        try:
            session = ReviewSession.objects.get(pk=pk)
        except ReviewSession.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if session.status != ReviewSession.Status.AWAITING_APPROVAL:
            return Response(
                {"detail": f"Cannot reject session with status '{session.status}'."},
                status=status.HTTP_409_CONFLICT,
            )

        session.status = ReviewSession.Status.FAILED
        session.save(update_fields=["status", "updated_at"])
        return Response({"id": session.id, "status": session.status})
