from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from ..models import AppointmentSlot


def get_available_slots_queryset():
    return AppointmentSlot.objects.select_related("doctor").filter(
        doctor__is_active=True,
        is_available=True,
        date__gte=timezone.localdate(),
    )


def get_user_home_url(user):
    if user.is_staff:
        return reverse("clinic:dashboard_home")
    return reverse("clinic:patient_home")


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy("clinic:login")

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()

        messages.error(
            self.request,
            "You do not have permission to access this page.",
        )
        return redirect("clinic:home")
