from django import forms
from .models import Company


class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = (
            "name",
            "website",
            "hr_email",
            "hr_phone_number",
        )