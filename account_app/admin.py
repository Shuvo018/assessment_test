from django.contrib import admin
from .models import User

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "username", "first_name", "last_name", "role", "is_active")
    search_fields = ("email", "username", "first_name", "last_name")
    list_filter = ("role", "is_active")
    ordering = ("-created_at",)

admin.site.register(User, UserAdmin)