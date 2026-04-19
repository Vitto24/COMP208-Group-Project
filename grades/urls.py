from django.urls import path
from . import views

app_name = 'grades'

urlpatterns = [
    path('', views.grades, name='grades'),
    path('submit/<int:assignment_id>/', views.submit_assignment, name='submit_assignment'),
    path('mark/<int:assignment_id>/', views.mark_assignment, name='mark_assignment'),
]
