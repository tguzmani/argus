from rest_framework import serializers

from apps.pulls.models import PullRequest


class PullRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PullRequest
        fields = [
            "id",
            "repository",
            "github_pr_number",
            "title",
            "description",
            "author",
            "base_branch",
            "head_branch",
            "github_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
