import time

from celery import shared_task

from apps.reviews.models import ReviewFinding, ReviewSession


@shared_task(bind=True)
def run_review(self, session_id: int) -> dict:
    session = ReviewSession.objects.get(pk=session_id)

    session.status = ReviewSession.Status.RUNNING
    session.celery_task_id = self.request.id
    session.save(update_fields=["status", "celery_task_id", "updated_at"])

    # Stub: simulate agent work
    time.sleep(3)

    # Create fake findings
    ReviewFinding.objects.create(
        review_session=session,
        severity=ReviewFinding.Severity.WARNING,
        file_path="src/utils/auth.py",
        line_number=42,
        comment_body="Consider using constant-time comparison for token validation.",
    )
    ReviewFinding.objects.create(
        review_session=session,
        severity=ReviewFinding.Severity.SUGGESTION,
        file_path="src/api/views.py",
        line_number=15,
        comment_body="This queryset could benefit from select_related to avoid N+1 queries.",
    )

    session.status = ReviewSession.Status.AWAITING_APPROVAL
    session.save(update_fields=["status", "updated_at"])

    return {"session_id": session_id, "status": session.status}
