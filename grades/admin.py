from django.contrib import admin
from .models import Assignment, Grade


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'weight', 'type', 'due_date')
    search_fields = ('title', 'module__code')
    list_filter = ('type', 'module__semester', 'module__academic_year')
    ordering = ('module', 'due_date')


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'score', 'status')
    search_fields = ('student__username', 'assignment__title')
    list_filter = ('status', 'assignment__module')
