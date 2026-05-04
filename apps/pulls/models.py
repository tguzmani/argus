from django.db import models


class PullRequest(models.Model):
    repository = models.ForeignKey(
        "repositories.Repository",
        on_delete=models.CASCADE,
        related_name="pull_requests",
    )
    github_pr_number = models.PositiveIntegerField()
    title = models.CharField(max_length=512)
    description = models.TextField(blank=True, default="")
    author = models.CharField(max_length=255)
    base_branch = models.CharField(max_length=255)
    head_branch = models.CharField(max_length=255)
    github_url = models.URLField(max_length=1024)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("repository", "github_pr_number")

    def __str__(self):
        return f"{self.repository.full_name}#{self.github_pr_number}"
