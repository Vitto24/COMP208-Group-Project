from django.urls import path
from . import views

app_name = 'settings_page'

urlpatterns = [
    path('', views.settings_view, name='settings'),
]
