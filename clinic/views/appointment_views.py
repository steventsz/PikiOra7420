from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from ..forms import AppointmentBookingForm
from ..models import Appointment, AppointmentSlot


class MyAppointmentsView(LoginRequiredMixin, ListView):
    template_name = "clinic/my_appointments.html"
    context_object_name = "appointments"
    login_url = reverse_lazy("clinic:login")

    def get_queryset(self):
        return (
            Appointment.objects.filter(patient=self.request.user)
            .select_related("slot", "slot__doctor")
            .order_by("slot__date", "slot__slot_index", "-created_at")
        )


class BookAppointmentView(LoginRequiredMixin, CreateView):
    form_class = AppointmentBookingForm
    template_name = "clinic/appointment_form.html"
    login_url = reverse_lazy("clinic:login")

    def dispatch(self, request, *args, **kwargs):
        self.slot = get_object_or_404(
            AppointmentSlot.objects.select_related("doctor"),
            pk=self.kwargs["slot_id"],
        )

        unavailable_redirect = self.get_unavailable_redirect()
        if unavailable_redirect:
            return unavailable_redirect

        return super().dispatch(request, *args, **kwargs)

    def get_unavailable_redirect(self):
        if self.slot.date < timezone.localdate():
            messages.error(
                self.request,
                "This appointment slot is already in the past.",
            )
            return redirect("clinic:slot_list")

        if not self.slot.doctor.is_active:
            messages.error(
                self.request,
                "This doctor is currently unavailable for new bookings.",
            )
            return redirect("clinic:doctor_detail", pk=self.slot.doctor.pk)

        if not self.slot.is_available:
            messages.error(
                self.request,
                "This appointment slot is no longer available.",
            )
            return redirect("clinic:doctor_detail", pk=self.slot.doctor.pk)

        if Appointment.objects.filter(slot=self.slot, status="booked").exists():
            self.slot.is_available = False
            self.slot.save(update_fields=["is_available"])
            messages.error(
                self.request,
                "This appointment slot has already been booked.",
            )
            return redirect("clinic:doctor_detail", pk=self.slot.doctor.pk)

        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Book Appointment"
        context["submit_label"] = "Confirm Booking"
        context["back_url"] = reverse("clinic:slot_list")
        context["slot"] = self.slot
        return context

    def form_valid(self, form):
        with transaction.atomic():
            slot = (
                AppointmentSlot.objects.select_for_update()
                .select_related("doctor")
                .get(pk=self.slot.pk)
            )

            if (
                slot.date < timezone.localdate()
                or not slot.doctor.is_active
                or not slot.is_available
            ):
                messages.error(
                    self.request,
                    "This appointment slot is no longer available.",
                )
                return redirect("clinic:slot_list")

            if Appointment.objects.filter(slot=slot, status="booked").exists():
                slot.is_available = False
                slot.save(update_fields=["is_available"])
                messages.error(
                    self.request,
                    "This appointment slot has already been booked.",
                )
                return redirect("clinic:slot_list")

            appointment = form.save(commit=False)
            appointment.patient = self.request.user
            appointment.slot = slot
            appointment.status = "booked"
            appointment.save()

            slot.is_available = False
            slot.save(update_fields=["is_available"])

        messages.success(self.request, "Appointment booked successfully.")
        return redirect("clinic:my_appointments")


class EditAppointmentView(LoginRequiredMixin, UpdateView):
    form_class = AppointmentBookingForm
    template_name = "clinic/appointment_form.html"
    login_url = reverse_lazy("clinic:login")
    success_url = reverse_lazy("clinic:my_appointments")

    def get_queryset(self):
        return Appointment.objects.filter(patient=self.request.user).select_related(
            "slot",
            "slot__doctor",
        )

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status != "booked":
            messages.error(request, "Only booked appointments can be edited.")
            return redirect("clinic:my_appointments")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Edit Appointment Notes"
        context["submit_label"] = "Save Changes"
        context["back_url"] = reverse("clinic:my_appointments")
        context["slot"] = self.object.slot
        return context

    def form_valid(self, form):
        messages.success(self.request, "Appointment notes updated successfully.")
        return super().form_valid(form)


class CancelAppointmentView(LoginRequiredMixin, View):
    login_url = reverse_lazy("clinic:login")
    template_name = "clinic/appointment_confirm_cancel.html"

    def get_appointment(self):
        return get_object_or_404(
            Appointment.objects.select_related("slot", "slot__doctor"),
            pk=self.kwargs["pk"],
            patient=self.request.user,
        )

    def get(self, request, pk):
        appointment = self.get_appointment()
        return render(
            request,
            self.template_name,
            {
                "appointment": appointment,
                "back_url": reverse("clinic:my_appointments"),
            },
        )

    def post(self, request, pk):
        appointment = self.get_appointment()

        if appointment.status != "booked":
            messages.error(request, "Only booked appointments can be cancelled.")
            return redirect("clinic:my_appointments")

        appointment.status = "cancelled"
        appointment.save(update_fields=["status", "updated_at"])

        appointment.slot.is_available = True
        appointment.slot.save(update_fields=["is_available"])

        messages.success(request, "Appointment cancelled successfully.")
        return redirect("clinic:my_appointments")
