from django.db import models


class Repository(models.Model):
    github_id = models.BigIntegerField(unique=True)
    owner = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=511, unique=True)
    default_branch = models.CharField(max_length=255, default="main")
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "repositories"

    def __str__(self):
        return self.full_name
