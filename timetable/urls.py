from django.urls import path
from . import views

app_name = 'timetable'

urlpatterns = [
    path('', views.timetable_view, name='timetable'),
    path('export.ics', views.export_ical, name='export_ical'),
]
