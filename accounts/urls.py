from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import EmailLoginForm
from . import views

app_name = 'accounts'

urlpatterns = [
    
    path('login/', views.login_view, name='login'), 
    
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('select-modules/', views.select_modules, name='select_modules'),
    path('randomise-modules/', views.randomise_modules, name='randomise_modules'),
    
    
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset_form.html',
        email_template_name='accounts/password_reset_email.html',
        success_url='/accounts/password_reset/done/',
        extra_context={'hide_sidebar': True}  
    ), name='password_reset'),
    
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html',
        extra_context={'hide_sidebar': True}  
    ), name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/accounts/reset/done/',
        extra_context={'hide_sidebar': True}  
    ), name='password_reset_confirm'),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html',
        extra_context={'hide_sidebar': True}  
    ), name='password_reset_complete'),
]