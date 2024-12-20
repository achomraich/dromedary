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

    path('dashboard/students/', views.StudentsView.as_view(), name='students_list'),
    path('dashboard/students/<int:student_id>/', views.StudentsView.as_view(), name='student_details'),
    path('dashboard/students/<int:student_id>/edit/', views.StudentsView.as_view(), name='student_edit'),
    path('dashboard/students/<int:student_id>/delete/', views.StudentsView.as_view(), name='student_delete'),
    path('dashboard/students/<int:student_id>/calendar/', views.StudentsView.as_view(), name='student_calendar'),
    path('dashboard/students/<int:student_id>/calendar/<int:year>/<int:month>/', views.StudentsView.as_view(), name='student_calendar'),


#<int:year>/<int:month>/
    path('dashboard/tutors/', views.TutorsView.as_view(), name='tutors_list'),
    path('dashboard/tutors/<int:tutor_id>/', views.TutorsView.as_view(), name='tutor_details'),
    path('dashboard/tutors/<int:tutor_id>/edit/', views.TutorsView.as_view(), name='tutor_edit'),
    path('dashboard/tutors/<int:tutor_id>/delete/', views.TutorsView.as_view(), name='tutor_delete'),
    path('dashboard/tutors/<int:tutor_id>/calendar/<int:year>/<int:month>/', views.TutorsView.as_view(), name='tutor_calendar'),
    path('dashboard/tutors/<int:tutor_id>/calendar/', views.TutorsView.as_view(), name='tutor_calendar'),


    path('dashboard/lessons/', views.ViewLessons.as_view(), name='lessons_list'),
    path('dashboard/lessons/<int:lesson_id>/', views.ViewLessons.as_view(), name='lesson_detail'),
    path('dashboard/lessons/<int:lesson_id>/update_feedback', views.ViewLessons.as_view(), name='update_feedback'),
    path('dashboard/lessons/<int:lesson_id>/request_changes/', views.UpdateLessonRequest.as_view(), name='request_changes'),
    path('dashboard/lessons/<int:lesson_id>/cancel_lesson', views.ViewLessons.as_view(), name='cancel_lesson'),

    path('dashboard/subjects/', views.SubjectView.as_view(), name='subjects_list'),
    path('dashboard/subjects/<int:subject_id>/edit/', views.SubjectView.as_view(), name='subject_edit'),
    path('dashboard/subjects/<int:subject_id>/delete/', views.SubjectView.as_view(), name='subject_delete'),
    path('dashboard/subjects/create', views.SubjectView.as_view(), name='new_subject'),

    path('dashboard/update_requests/', views.UpdateLessonRequest.as_view(), name='update_requests'),
    path('dashboard/update_requests/<int:lesson_id>/', views.UpdateLesson.as_view(), name='update_lesson'),

    path('dashboard/calendar/', views.Calendar.as_view(), name='calendar'),
    path('dashboard/calendar/<int:year>/<int:month>/', views.Calendar.as_view(), name='calendar'),

    path('dashboard/requests/', views.RequestView.as_view(), name='requests'),
    path('dashboard/request/', views.MakeRequestView.as_view(), name='lesson_request'),
    path('dashboard/request/<int:request_id>/assign/', views.RequestView.as_view(), name='request_assign'),

    path('availability/', views.AvailabilityView.as_view(), name='availability'),
    path('availability/add/', views.AddEditAvailabilityView.as_view(), name='availability_add'),
    path('availability/edit/<int:pk>/', views.AddEditAvailabilityView.as_view(), name='availability_edit'),

    path('invoices/', views.InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/create/', views.CreateInvoiceView.as_view(), name='create_invoice'),
    path('invoices/<int:invoice_id>/', views.InvoiceDetailView.as_view(), name='invoice_detail'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

