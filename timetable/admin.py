from django.contrib import admin
from .models import TimetableEntry


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ('student', 'module', 'day', 'start_time', 'end_time', 'semester', 'event_type', 'room')
    search_fields = ('student__username', 'module__code', 'room')
    list_filter = ('day', 'semester', 'event_type')
