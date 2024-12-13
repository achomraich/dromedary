from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View

from tutorials.forms import SubjectForm
from tutorials.models import Subject


"""
This file contains a view class to handle 
Subjects
"""

class SubjectView(View):
    """Allowing Admins to view, edit and delete subjects."""
    def get(self, request, subject_id=None):
        """Get a list of all subjects."""
        if request.path.endswith('create'):
            return self.create_subject(request)

        if subject_id:
            return self.edit_subject(request, subject_id)

        if hasattr(request.user, 'admin_profile'):
            self.list_of_subjects = Subject.objects.all()

            paginator = Paginator(self.list_of_subjects.order_by('name'), 20)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            return render(request, 'admin/manage_subjects/subjects_list.html', {'page_obj': page_obj})
        return HttpResponseForbidden("You do not have permission to view this page.")

    def post(self, request, subject_id=None):
        """Handle POST actions to create, edit or delete subjects."""
        if 'create' in request.path:
            return self.create_subject(request)
        if subject_id:
            if request.path.endswith('edit/'):
                return self.edit_subject(request, subject_id)
            else:
                subject = get_object_or_404(Subject, pk=subject_id)
                return self.delete_subject(request, subject)

        return redirect('subjects_list')

    def delete_subject(self, request, subject):
        """Deletes a subject."""
        subject.delete()
        return redirect('subjects_list')

    def handle_subject_form(self, request, subject=None):
        """Process subject form for adding or editing."""
        form = SubjectForm(request.POST or None, instance=subject)

        if form.is_valid():
            try:
                form.save()
                return HttpResponseRedirect(reverse('subjects_list'))
            except:
                form.add_error(None, "It was not possible to update this subject")
        return form

    def edit_subject(self, request, subject_id):
        """Edits a subject."""
        subject = get_object_or_404(Subject, pk=subject_id)
        form = self.handle_subject_form(request, subject)

        if isinstance(form, HttpResponseRedirect):
            return form

        return render(request, 'admin/manage_subjects/subject_edit.html', {'form': form, 'subject': subject})

    def create_subject(self, request):
        """Show form to create new subject."""
        form = self.handle_subject_form(request)
        if isinstance(form, HttpResponseRedirect):  # Redirect if the form is valid
            return form
        return render(request, 'admin/manage_subjects/subject_create.html', {'form': form})