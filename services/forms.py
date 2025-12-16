from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['address', 'preferred_date', 'preferred_time', 'notes']

    def clean(self):
        cleaned = super().clean()

        if not cleaned.get('address'):
            raise forms.ValidationError("Address is required")

        if not cleaned.get('preferred_date'):
            raise forms.ValidationError("Date is required")

        if not cleaned.get('preferred_time'):
            raise forms.ValidationError("Time is required")

        return cleaned
