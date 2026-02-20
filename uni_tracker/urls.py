from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('modules/', include('modules.urls')),
    path('grades/', include('grades.urls')),
    path('accounts/', include('accounts.urls')),
    path('settings/', include('settings_page.urls')),
    path('timetable/', include('timetable.urls')),
]
