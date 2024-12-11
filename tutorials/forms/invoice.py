from datetime import date

from django import forms

from tutorials.models import Invoice, Student, Subject


class InvoiceForm(forms.ModelForm):
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        empty_label="Select a lesson...",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Invoice
        fields = ['student', 'amount', 'due_date', 'status']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.select_related('user').all()
        self.fields['student'].label_from_instance = lambda obj: f"{obj.user.username} ({obj.user.full_name()})"
        self.fields['subject'].queryset = Subject.objects.all()
        self.fields['subject'].label_from_instance = lambda obj: f"{obj.name}"

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero")
        return amount

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < date.today():
            raise forms.ValidationError("Due date cannot be in the past")
        return due_date