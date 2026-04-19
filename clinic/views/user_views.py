from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, TemplateView

from ..forms import PatientRegisterForm
from ..models import Appointment, Doctor
from .common import get_available_slots_queryset, get_user_home_url


class HomeView(TemplateView):
    template_name = "clinic/home.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(get_user_home_url(request.user))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_doctors_count"] = Doctor.objects.filter(is_active=True).count()
        context["available_slots_count"] = get_available_slots_queryset().count()
        return context


class RoleBasedLoginView(LoginView):
    template_name = "clinic/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or get_user_home_url(self.request.user)


class PatientRegisterView(CreateView):
    form_class = PatientRegisterForm
    template_name = "clinic/register.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(get_user_home_url(request.user))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        messages.success(
            self.request,
            "Registration successful. You are now logged in.",
        )
        return redirect(get_user_home_url(self.object))


class PatientHomeView(LoginRequiredMixin, TemplateView):
    template_name = "clinic/patient_home.html"
    login_url = reverse_lazy("clinic:login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff:
            return redirect("clinic:dashboard_home")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["upcoming_appointments_count"] = Appointment.objects.filter(
            patient=self.request.user,
            status="booked",
            slot__date__gte=timezone.localdate(),
        ).count()
        context["active_doctors_count"] = Doctor.objects.filter(is_active=True).count()
        context["available_slots_count"] = get_available_slots_queryset().count()
        return context
