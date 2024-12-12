from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from tutorials.forms import InvoiceForm
from tutorials.models import Invoice, LessonStatus, Student


"""
This file contains classes to handle 
1- Invoices view
2- Create Invoices
3- Invoice details
"""

class InvoiceListView(LoginRequiredMixin, View):
    ''' Handeles list of invoices '''
    def get(self, request):
        invoice_list = Invoice.objects.all().order_by('-created_at')
        paginator = Paginator(invoice_list, 10)  # Show 10 invoices per page

        page = request.GET.get('page')
        invoices = paginator.get_page(page)

        return render(request, 'invoices/invoice_list.html', {'invoices': invoices})


class CreateInvoiceView(LoginRequiredMixin, View):
    """ Allowes admin to generate an invoice for students """
    def get(self, request):
        form = InvoiceForm()
        return render(request, 'invoices/create_invoice.html', {'form': form})

    def post(self, request):
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)

            # Get uninvoiced lessons for the student
            uninvoiced_lessons = LessonStatus.objects.filter(
                lesson_id__student=invoice.student,
                invoiced=False
            )

            if not uninvoiced_lessons.exists():
                messages.error(request, "No uninvoiced lessons found for this student.")
                return render(request, 'invoices/create_invoice.html', {'form': form})

            invoice.save()
            invoice.lessons.set(uninvoiced_lessons)
            messages.success(request, f"Invoice #{invoice.id} created successfully.")
            return redirect('invoice_list')

        return render(request, 'invoices/create_invoice.html', {'form': form})


class InvoiceDetailView(LoginRequiredMixin, View):
    """ Views the invoice details """
    def get(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, id=invoice_id)

        return render(request, 'invoices/invoice_detail.html', {'invoice': invoice})

    def post(self, request, invoice_id):
        ''' Allows admin to edit the invoice or delete it '''
        invoice = get_object_or_404(Invoice, id=invoice_id)
        if 'delete' in request.POST:
            invoice.delete()
            messages.success(request, f'Invoice #{invoice_id} deleted successfully')
            return redirect('invoice_list')
        elif 'mark_paid' in request.POST:
            invoice.mark_as_paid()
            messages.success(request, f'Invoice #{invoice_id} marked as paid')
            return redirect('invoice_list')
        return redirect('invoice_detail', invoice_id=invoice_id)


@login_required
def invoice_management(request):
    invoices = Invoice.objects.all().order_by('-created_at')
    return render(request, 'invoices/invoice_list.html', {'invoices': invoices})

@login_required
def create_invoice(request):

    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            subject = form.cleaned_data['subject']
            invoice.save()

            # Link lessons
            lessons = LessonStatus.objects.filter(
                lesson_id__student=invoice.student,
                lesson_id__subject_id=subject,
                invoiced=False
            )
            if lessons.exists():
                invoice.lessons.set(lessons)
                lessons.update(invoiced=True)
                messages.success(request, f'Invoice #{invoice.id} created successfully')
            else:
                messages.warning(request, 'No uninvoiced lessons found for selected student and subject')
            return redirect('invoice_list')
        else:
            print("Form errors:", form.errors)
    else:
        form = InvoiceForm()

    return render(request, 'invoices/create_invoice.html', {'form': form})

@login_required
def invoice_list(request):
    # Make sure we're getting all related data in one query
    invoices = (Invoice.objects
                .select_related('student__user')
                .prefetch_related('lessons')
                .all()
                .order_by('-created_at'))

    return render(request, 'invoices/invoice_list.html', {
        'invoices': invoices
    })

    # Extract form data
    student_username = request.POST.get('student')
    amount = request.POST.get('amount')
    due_date = request.POST.get('due_date')
    is_paid = request.POST.get('is_paid') == 'on'

    # Get the User instance based on the provided student username
    student = get_object_or_404(User, username=student_username)

    # Create a new Invoice record
    Invoice.objects.create(
        student=student,  # Use the User instance here
        amount=amount,
        due_date=due_date,
        is_paid=is_paid
    )

    # Redirect back to the invoice management page
    return redirect('invoice_management')