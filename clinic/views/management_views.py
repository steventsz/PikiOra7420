from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)

from ..forms import (
    AdminAppointmentUpdateForm,
    AppointmentSlotForm,
    DoctorForm,
    PatientUpdateForm,
)
from ..models import Appointment, AppointmentSlot, Doctor
from .common import StaffRequiredMixin


class DashboardHomeView(StaffRequiredMixin, TemplateView):
    template_name = "clinic/dashboard/dashboard_home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_doctors"] = Doctor.objects.count()
        context["total_patients"] = User.objects.filter(is_staff=False).count()
        context["total_slots"] = AppointmentSlot.objects.count()
        context["total_booked_appointments"] = Appointment.objects.filter(
            status="booked"
        ).count()
        return context


class DashboardDoctorListView(StaffRequiredMixin, ListView):
    model = Doctor
    template_name = "clinic/dashboard/doctor_list.html"
    context_object_name = "doctors"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_doctors_count"] = Doctor.objects.filter(is_active=True).count()
        return context


class DashboardDoctorCreateView(StaffRequiredMixin, CreateView):
    form_class = DoctorForm
    template_name = "clinic/dashboard/form.html"
    success_url = reverse_lazy("clinic:dashboard_doctor_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Add Doctor"
        context["back_url"] = reverse("clinic:dashboard_doctor_list")
        return context

    def form_valid(self, form):
        messages.success(self.request, "Doctor created successfully.")
        return super().form_valid(form)


class DashboardDoctorUpdateView(StaffRequiredMixin, UpdateView):
    model = Doctor
    form_class = DoctorForm
    template_name = "clinic/dashboard/form.html"
    success_url = reverse_lazy("clinic:dashboard_doctor_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Edit Doctor"
        context["back_url"] = reverse("clinic:dashboard_doctor_list")
        return context

    def form_valid(self, form):
        messages.success(self.request, "Doctor updated successfully.")
        return super().form_valid(form)


class DashboardDoctorDeleteView(StaffRequiredMixin, DeleteView):
    model = Doctor
    template_name = "clinic/dashboard/confirm_delete.html"
    success_url = reverse_lazy("clinic:dashboard_doctor_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Delete Doctor"
        context["back_url"] = reverse("clinic:dashboard_doctor_list")
        context["object_label"] = self.object.name
        context["warning_text"] = (
            "Deleting this doctor will also remove slots that do not have "
            "appointment records."
        )
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if Appointment.objects.filter(slot__doctor=self.object).exists():
            messages.error(
                request,
                "This doctor cannot be deleted because appointment records already exist.",
            )
            return redirect("clinic:dashboard_doctor_list")

        messages.success(request, "Doctor deleted successfully.")
        return super().post(request, *args, **kwargs)


class DashboardSlotListView(StaffRequiredMixin, ListView):
    template_name = "clinic/dashboard/slot_list.html"
    context_object_name = "slots"

    def get_queryset(self):
        return AppointmentSlot.objects.select_related("doctor").order_by(
            "date",
            "slot_index",
            "doctor__name",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["available_slots_count"] = AppointmentSlot.objects.filter(
            is_available=True
        ).count()
        return context


class DashboardSlotCreateView(StaffRequiredMixin, CreateView):
    form_class = AppointmentSlotForm
    template_name = "clinic/dashboard/form.html"
    success_url = reverse_lazy("clinic:dashboard_slot_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Add Appointment Slot"
        context["back_url"] = reverse("clinic:dashboard_slot_list")
        return context

    def form_valid(self, form):
        messages.success(self.request, "Appointment slot created successfully.")
        return super().form_valid(form)


class DashboardSlotUpdateView(StaffRequiredMixin, UpdateView):
    model = AppointmentSlot
    form_class = AppointmentSlotForm
    template_name = "clinic/dashboard/form.html"
    success_url = reverse_lazy("clinic:dashboard_slot_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Edit Appointment Slot"
        context["back_url"] = reverse("clinic:dashboard_slot_list")
        return context

    def form_valid(self, form):
        messages.success(self.request, "Appointment slot updated successfully.")
        return super().form_valid(form)


class DashboardSlotDeleteView(StaffRequiredMixin, DeleteView):
    model = AppointmentSlot
    template_name = "clinic/dashboard/confirm_delete.html"
    success_url = reverse_lazy("clinic:dashboard_slot_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Delete Slot"
        context["back_url"] = reverse("clinic:dashboard_slot_list")
        context["object_label"] = (
            f"{self.object.doctor.name} - {self.object.date} - "
            f"{self.object.get_slot_index_display()}"
        )
        context["warning_text"] = "Only unused slots should be deleted."
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.appointments.exists():
            messages.error(
                request,
                "This slot cannot be deleted because appointment records already exist.",
            )
            return redirect("clinic:dashboard_slot_list")

        messages.success(request, "Appointment slot deleted successfully.")
        return super().post(request, *args, **kwargs)


class DashboardAppointmentListView(StaffRequiredMixin, ListView):
    template_name = "clinic/dashboard/appointment_list.html"
    context_object_name = "appointments"

    def get_queryset(self):
        return Appointment.objects.select_related(
            "patient",
            "slot",
            "slot__doctor",
        ).order_by("slot__date", "slot__slot_index", "-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["booked_appointments_count"] = Appointment.objects.filter(
            status="booked"
        ).count()
        return context


class DashboardAppointmentUpdateView(StaffRequiredMixin, UpdateView):
    model = Appointment
    form_class = AdminAppointmentUpdateForm
    template_name = "clinic/dashboard/form.html"
    success_url = reverse_lazy("clinic:dashboard_appointment_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Update Appointment"
        context["back_url"] = reverse("clinic:dashboard_appointment_list")
        context["appointment"] = self.object
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.slot.is_available = self.object.status == "cancelled"
        self.object.slot.save(update_fields=["is_available"])
        messages.success(self.request, "Appointment updated successfully.")
        return response


class DashboardAppointmentCancelView(StaffRequiredMixin, View):
    template_name = "clinic/dashboard/appointment_confirm_cancel.html"

    def get_appointment(self):
        return get_object_or_404(
            Appointment.objects.select_related("patient", "slot", "slot__doctor"),
            pk=self.kwargs["pk"],
        )

    def get(self, request, pk):
        appointment = self.get_appointment()
        return render(
            request,
            self.template_name,
            {
                "appointment": appointment,
                "back_url": reverse("clinic:dashboard_appointment_list"),
            },
        )

    def post(self, request, pk):
        appointment = self.get_appointment()

        if appointment.status != "booked":
            messages.error(request, "Only booked appointments can be cancelled.")
            return redirect("clinic:dashboard_appointment_list")

        appointment.status = "cancelled"
        appointment.save(update_fields=["status", "updated_at"])
        appointment.slot.is_available = True
        appointment.slot.save(update_fields=["is_available"])

        messages.success(request, "Appointment cancelled successfully.")
        return redirect("clinic:dashboard_appointment_list")


class DashboardPatientListView(StaffRequiredMixin, ListView):
    template_name = "clinic/dashboard/patient_list.html"
    context_object_name = "patients"

    def get_queryset(self):
        return User.objects.filter(is_staff=False).order_by("username")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_patients_count"] = User.objects.filter(
            is_staff=False,
            is_active=True,
        ).count()
        return context


class DashboardPatientUpdateView(StaffRequiredMixin, UpdateView):
    model = User
    form_class = PatientUpdateForm
    template_name = "clinic/dashboard/form.html"
    success_url = reverse_lazy("clinic:dashboard_patient_list")

    def get_queryset(self):
        return User.objects.filter(is_staff=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Edit Patient"
        context["back_url"] = reverse("clinic:dashboard_patient_list")
        return context

    def form_valid(self, form):
        messages.success(self.request, "Patient account updated successfully.")
        return super().form_valid(form)
