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

    path('dashboard/tutors/', views.TutorsView.as_view(), name='tutors_list'),
    path('dashboard/tutors/<int:tutor_id>/', views.TutorsView.as_view(), name='tutor_details'),
    path('dashboard/tutors/<int:tutor_id>/edit/', views.TutorsView.as_view(), name='tutor_edit'),
    path('dashboard/tutors/<int:tutor_id>/delete/', views.TutorsView.as_view(), name='tutor_delete'),

    path('dashboard/lessons/', views.ViewLessons.as_view(), name='lessons_list'),
    path('dashboard/lessons/<int:lesson_id>/', views.ViewLessons.as_view(), name='lesson_detail'),
    path('dashboard/lessons/<int:lesson_id>/update_feedback', views.ViewLessons.as_view(), name='update_feedback'),
    path('dashboard/lessons/<int:lesson_id>/request_changes/', views.UpdateLessonRequest.as_view(), name='request_changes'),

    path('dashboard/subjects/', views.SubjectView.as_view(), name='subjects_list'),
    path('dashboard/subjects/<int:subject_id>/edit/', views.SubjectView.as_view(), name='subject_edit'),
    path('dashboard/subjects/<int:subject_id>/delete/', views.SubjectView.as_view(), name='subject_delete'),
    path('dashboard/subject/create', views.SubjectView.as_view(), name='new_subject'),

    path('dashboard/update_requests/', views.UpdateLessonRequest.as_view(), name='update_requests'),
    path('dashboard/requests/', views.LessonRequest, name='admin_lesson_requests'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)