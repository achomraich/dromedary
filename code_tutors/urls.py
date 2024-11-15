"""
URL configuration for code_tutors project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from tutorials import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/tutor/', views.tutor_dashboard, name='tutor_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('invoices/', views.invoice_management, name='invoice_management'),
    path('invoices/create/', views.create_invoice, name='create_invoice'),  # URL pattern for creating invoices
    path('dashboard/students/', views.StudentsView.as_view(), name='students_list'),
    path('dashboard/students/<int:student_id>/', views.StudentsView.as_view(), name='student_details'),
    path('dashboard/students/<int:student_id>/edit/', views.StudentsView.as_view(), name='student_edit'),
    path('dashboard/students/<int:student_id>/delete/', views.StudentsView.as_view(), name='student_delete'),
    path('dashboard/lessons/', views.ViewLessons.as_view(), name='lessons_list'),
    path('dashboard/tutors/', views.AdminTutors.as_view(), name='tutors_list'),
    path('dashboard/lessons/<int:lesson_id>/', views.ViewLessons.as_view(), name='lesson_detail'),
    path('requests/', views.lesson_requests, name='requests'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)