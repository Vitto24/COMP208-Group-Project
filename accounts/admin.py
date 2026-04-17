from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'role', 'course', 'year_of_study', 'university', 'study_level')
    search_fields = ('user__username', 'user__email', 'student_id')
    list_filter = ('role', 'university', 'study_level', 'year_of_study')
