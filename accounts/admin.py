from django.contrib import admin
from .models import UserProfile

if admin.site.is_registered(UserProfile):
    admin.site.unregister(UserProfile)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('student_id',)
    fields = ('user', 'role', 'university', 'course', 'year_of_study', 'degree_level', 'student_id')