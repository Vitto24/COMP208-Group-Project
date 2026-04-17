from django.contrib import admin
from .models import Module, Week, Material, Course, ModuleCourse


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'credits', 'semester', 'academic_year', 'department')
    search_fields = ('code', 'name', 'department')
    list_filter = ('semester', 'academic_year', 'year')
    ordering = ('code',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'degree_level', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('degree_level',)


@admin.register(ModuleCourse)
class ModuleCourseAdmin(admin.ModelAdmin):
    list_display = ('module', 'course', 'year', 'is_compulsory')
    search_fields = ('module__code', 'course__name')
    list_filter = ('year', 'is_compulsory', 'course')


@admin.register(Week)
class WeekAdmin(admin.ModelAdmin):
    list_display = ('module', 'number', 'title')
    search_fields = ('module__code', 'title')
    list_filter = ('module',)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'week', 'type', 'available')
    search_fields = ('title',)
    list_filter = ('type', 'available')
