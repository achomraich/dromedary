from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from tutorials.forms import InvoiceForm
from tutorials.models import Invoice, LessonStatus, Student


"""
This file contains view classes and functions to handle 
1 - Invoices view
2 - Create Invoices
3 - Invoice details
"""

class InvoiceListView(LoginRequiredMixin, View):
    """Handles list of invoices."""
    def get(self, request):
        invoice_list = Invoice.objects.all().order_by('-created_at')
        paginator = Paginator(invoice_list, 10)  # Show 10 invoices per page

        page = request.GET.get('page')
        invoices = paginator.get_page(page)

        return render(request, 'invoices/invoice_list.html', {'invoices': invoices})


class CreateInvoiceView(LoginRequiredMixin, View):
    """Allows admin to generate an invoice for students."""
    def get(self, request):
        """Display a form to create an invoice."""
        form = InvoiceForm()
        return render(request, 'invoices/create_invoice.html', {'form': form})

    def post(self, request):
        """Process the form to create an invoice."""
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
    """View the invoice details."""
    def get(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, id=invoice_id)

        return render(request, 'invoices/invoice_detail.html', {'invoice': invoice})

    def post(self, request, invoice_id):
        """Allows admin to edit the invoice or delete it."""
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
