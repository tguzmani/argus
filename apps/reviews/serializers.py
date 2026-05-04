from rest_framework import serializers

from apps.reviews.models import ReviewFinding, ReviewSession


class ReviewFindingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewFinding
        fields = [
            "id",
            "severity",
            "status",
            "file_path",
            "line_number",
            "comment_body",
            "github_comment_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReviewSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewSession
        fields = [
            "id",
            "pull_request",
            "thread_id",
            "status",
            "celery_task_id",
            "total_tokens_used",
            "total_cost_usd",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "thread_id",
            "status",
            "celery_task_id",
            "total_tokens_used",
            "total_cost_usd",
            "created_at",
            "updated_at",
        ]


class ReviewSessionDetailSerializer(serializers.ModelSerializer):
    findings = ReviewFindingSerializer(many=True, read_only=True)

    class Meta:
        model = ReviewSession
        fields = [
            "id",
            "pull_request",
            "thread_id",
            "status",
            "celery_task_id",
            "total_tokens_used",
            "total_cost_usd",
            "findings",
            "created_at",
            "updated_at",
        ]
