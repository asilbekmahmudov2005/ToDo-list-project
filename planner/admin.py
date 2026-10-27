from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'date', 'priority', 'category', 'is_completed')
    list_filter = ('is_completed', 'priority', 'category', 'date')
    search_fields = ('title', 'description', 'user__username')
    ordering = ('-date', '-created_at')
