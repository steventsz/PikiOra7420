from django.views.generic import DetailView, ListView

from ..models import Doctor
from .common import get_available_slots_queryset


class DoctorListView(ListView):
    model = Doctor
    template_name = "clinic/doctor_list.html"
    context_object_name = "doctors"

    def get_queryset(self):
        return Doctor.objects.filter(is_active=True).order_by("name")


class DoctorDetailView(DetailView):
    model = Doctor
    template_name = "clinic/doctor_detail.html"
    context_object_name = "doctor"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["available_slots"] = get_available_slots_queryset().filter(
            doctor=self.object
        ).order_by("date", "slot_index")
        return context


class SlotListView(ListView):
    template_name = "clinic/slot_list.html"
    context_object_name = "slots"

    def get_queryset(self):
        queryset = get_available_slots_queryset().order_by(
            "date",
            "slot_index",
            "doctor__name",
        )
        doctor_id = self.request.GET.get("doctor")
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["doctors"] = Doctor.objects.filter(is_active=True).order_by("name")
        context["selected_doctor"] = self.request.GET.get("doctor", "")
        return context
