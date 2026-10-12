from rest_framework import serializers

from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            "id",
            "company",
            "role",
            "status",
            "priority",
            "source",
            "salary",
            "location",
            "url",
            "notes",
            "applied_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_applied_at(self, value):
        """Require applied_at whenever status is applied or beyond wishlist."""
        if value:
            return value
        status = self.initial_data.get("status")
        if status and status not in (Application.Status.WISHLIST, ""):
            raise serializers.ValidationError(
                "applied_at is required for statuses beyond wishlist."
            )
        return value
