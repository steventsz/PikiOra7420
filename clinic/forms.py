from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Appointment, AppointmentSlot, Doctor


class PatientRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False, max_length=150)
    last_name = forms.CharField(required=False, max_length=150)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        # Check email uniqueness at form level because Django's default User model
        # does not enforce a unique email field for us.
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        # Reuse UserCreationForm's built-in password handling, then fill in the
        # extra profile fields required by this project.
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"].strip()
        user.last_name = self.cleaned_data["last_name"].strip()
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class PatientAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["notes"]
        widgets = {
            "notes": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Optional notes for the doctor",
                }
            ),
        }


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ["name", "specialty", "bio", "email", "phone", "is_active"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }


class AppointmentSlotForm(forms.ModelForm):
    class Meta:
        model = AppointmentSlot
        fields = ["doctor", "date", "slot_index", "is_available"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_date(self):
        date = self.cleaned_data["date"]
        # Slot management should stay realistic, so admins cannot create slots
        # for dates that have already passed.
        if date < timezone.localdate():
            raise ValidationError("Appointment slots cannot be created in the past.")
        return date

    def clean(self):
        # Keep Django's default form cleaning, then add our own conflict check.
        cleaned_data = super().clean()
        doctor = cleaned_data.get("doctor")
        date = cleaned_data.get("date")
        slot_index = cleaned_data.get("slot_index")

        if not all([doctor, date, slot_index]):
            return cleaned_data

        duplicate_slot = AppointmentSlot.objects.filter(
            doctor=doctor,
            date=date,
            slot_index=slot_index,
        )
        if self.instance.pk:
            duplicate_slot = duplicate_slot.exclude(pk=self.instance.pk)

        if duplicate_slot.exists():
            raise ValidationError(
                "This doctor already has a slot scheduled for that date and time."
            )

        return cleaned_data


class AdminAppointmentUpdateForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["status", "notes"]
        widgets = {
            "notes": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Internal or patient-facing notes",
                }
            ),
        }

    def clean(self):
        # Keep the base cleaning result, then make sure a slot cannot end up
        # with more than one active booked appointment.
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        slot = self.instance.slot

        if status == "booked":
            other_booked_appointment = Appointment.objects.filter(
                slot=slot,
                status="booked",
            )
            if self.instance.pk:
                other_booked_appointment = other_booked_appointment.exclude(
                    pk=self.instance.pk
                )

            if other_booked_appointment.exists():
                raise ValidationError(
                    "This slot already has an active booked appointment."
                )

        return cleaned_data


class PatientUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "is_active"]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if not email:
            return email

        # Exclude the current user so keeping the original email does not fail.
        duplicate_user = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            duplicate_user = duplicate_user.exclude(pk=self.instance.pk)

        if duplicate_user.exists():
            raise ValidationError("A user with this email already exists.")
        return email


# Backward-compatible alias for the existing booking view.
AppointmentBookingForm = PatientAppointmentForm
