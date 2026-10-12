from django.contrib import admin

from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("company", "role", "user", "status", "priority", "updated_at")
    list_filter = ("status", "priority")
    search_fields = ("company", "role", "notes")
