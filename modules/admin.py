from django.contrib import admin
from .models import Module, Week, Material, Course, ModuleCourse

admin.site.register(Module)
admin.site.register(Week)
admin.site.register(Material)
admin.site.register(Course)
admin.site.register(ModuleCourse)
