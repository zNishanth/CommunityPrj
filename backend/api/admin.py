from django.contrib import admin
from .models import User, ReportedURL

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "username", "is_active", "is_superuser"]

@admin.register(ReportedURL)
class ReportedURLAdmin(admin.ModelAdmin):
    list_display = ["url", "user", "reported_date", "confirmed", "chain_tx_hash"]
    list_filter = ["confirmed"]
