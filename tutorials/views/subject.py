from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View

from tutorials.forms import SubjectForm
from tutorials.models import Subject


class SubjectView(View):

    def get(self, request, subject_id=None):
        if subject_id:
            return self.edit_subject(request, subject_id)

        if hasattr(request.user, 'admin_profile'):
            self.list_of_subjects = Subject.objects.all().order_by('name')

            paginator = Paginator(self.list_of_subjects, 20)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            return render(request, 'admin/manage_subjects/subjects_list.html', {'page_obj': page_obj})
        return HttpResponseForbidden("You do not have permission to view this page.")

    def post(self, request, subject_id=None):
        if 'create' in request.path:
            return self.create_subject(request)

        if subject_id:
            if request.path.endswith('edit/'):
                return self.edit_subject(request, subject_id)
            elif request.path.endswith('delete/'):
                subject = get_object_or_404(Subject, pk=subject_id)
                return self.delete_subject(request, subject)

        return redirect('subjects_list')

    def delete_subject(self, request, subject):
        subject.delete()
        return redirect('subjects_list')

    def handle_subject_form(self, request, subject=None):
        form = SubjectForm(request.POST or None, instance=subject)

        if form.is_valid():
            try:
                form.save()
                return HttpResponseRedirect(reverse('subjects_list'))
            except:
                form.add_error(None, "It was not possible to update this subject")
        return form

    def edit_subject(self, request, subject_id):
        subject = get_object_or_404(Subject, pk=subject_id)
        form = self.handle_subject_form(request, subject)

        if isinstance(form, HttpResponseRedirect):
            return form

        return render(request, 'admin/manage_subjects/subject_edit.html', {'form': form, 'subject': subject})

    def create_subject(self, request):
        form = self.handle_subject_form(request)
        if isinstance(form, HttpResponseRedirect):  # Redirect if the form is valid
            return form
        return render(request, 'admin/manage_subjects/subject_create.html', {'form': form})
