from django.db import models
from django.conf import settings


from django.db.models.functions import Lower


class Application(models.Model):
    """One job application the user is tracking."""

    class Status(models.TextChoices):
        WISHLIST = "wishlist", "Wishlist"
        APPLIED = "applied", "Applied"
        INTERVIEW = "interview", "Interview"
        OFFER = "offer", "Offer"
        REJECTED = "rejected", "Rejected"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    company = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.WISHLIST
    )
    priority = models.CharField(
        max_length=20, choices=Priority.choices, default=Priority.MEDIUM
    )
    source = models.CharField(max_length=200, blank=True)
    salary = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    applied_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                Lower("company"), Lower("role"), "user", name="uniq_user_company_role"
            )
        ]

    def __str__(self):
        return f"{self.company} — {self.role} ({self.get_status_display()})"
