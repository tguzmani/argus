import uuid

from django.db import models


class ReviewSession(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending"
        RUNNING = "running"
        AWAITING_APPROVAL = "awaiting_approval"
        APPROVED = "approved"
        POSTED = "posted"
        FAILED = "failed"

    pull_request = models.ForeignKey(
        "pulls.PullRequest",
        on_delete=models.CASCADE,
        related_name="review_sessions",
    )
    thread_id = models.UUIDField(default=uuid.uuid4, unique=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    celery_task_id = models.CharField(max_length=255, blank=True, default="")
    total_tokens_used = models.PositiveIntegerField(default=0)
    total_cost_usd = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review {self.id} for {self.pull_request}"


class ReviewFinding(models.Model):
    class Severity(models.TextChoices):
        CRITICAL = "critical"
        WARNING = "warning"
        SUGGESTION = "suggestion"

    class Status(models.TextChoices):
        DRAFT = "draft"
        APPROVED = "approved"
        REJECTED = "rejected"
        POSTED = "posted"

    review_session = models.ForeignKey(
        ReviewSession,
        on_delete=models.CASCADE,
        related_name="findings",
    )
    severity = models.CharField(max_length=10, choices=Severity.choices)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    file_path = models.CharField(max_length=1024)
    line_number = models.PositiveIntegerField(null=True, blank=True)
    comment_body = models.TextField()
    github_comment_id = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.severity} at {self.file_path}:{self.line_number}"


class AgentStep(models.Model):
    review_session = models.ForeignKey(
        ReviewSession,
        on_delete=models.CASCADE,
        related_name="steps",
    )
    node_name = models.CharField(max_length=255)
    tokens_used = models.PositiveIntegerField(default=0)
    duration_ms = models.PositiveIntegerField(default=0)
    error = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.node_name} (session {self.review_session_id})"
