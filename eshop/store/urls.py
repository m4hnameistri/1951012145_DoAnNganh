from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from .forms import (UserLoginForm, ResetPasswordForm, ResetConfirmForm)

app_name = 'store'
urlpatterns = [
    path('', views.product_all, name = 'product_all'),
    path('item/<slug:slug>/', views.product_detail, name = 'product_detail'),
    path('search/<slug:category_slug>/', views.category_list, name='category_list'),
    path('account/register/', views.user_register, name='register'),
    path('account/<slug:uidb64>/<slug:token>/', views.user_activate, name='activate'),
    path('account/dashboard/', views.dashboard, name = 'dashboard'),
    path('account/login/', auth_views.LoginView.as_view(template_name='account/login.html',
    form_class = UserLoginForm), name = 'login'),
    path('account/logout/', auth_views.LogoutView.as_view(next_page='store:login'),
    name = 'logout'),
    path('account/password_reset/', auth_views.PasswordResetView.as_view(template_name='account/password_reset_form.html',
                                                                        success_url = 'password_reset_email_confirm',
                                                                        email_template_name = 'account/password_reset_email.html',
                                                                        form_class = ResetPasswordForm), name = 'password_reset'),
    path('account/password_reset/password_reset_email_confirm/', TemplateView.as_view(template_name = 'account/reset_status.html'), name = 'password_reset_done'),
    path('account/password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name= 'account/password_reset_confirm.html',
                                                                                                        success_url = '/account/password_reset_complete',
                                                                                                        form_class = ResetConfirmForm), name = 'password_reset_confirm'),
    path('account/password_reset_complete/', TemplateView.as_view(template_name="account/reset_status.html"), name='password_reset_complete'),
    path('account/profile/', views.profile, name = 'profile'),
    path('account/edit_info/', views.edit_info, name = 'edit_info'),
    path('search',views.search,name='search'),

]