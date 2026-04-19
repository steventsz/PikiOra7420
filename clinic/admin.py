from django.contrib import admin

from .models import Appointment, AppointmentSlot, Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("name", "specialty", "email", "phone", "is_active")
    list_filter = ("is_active", "specialty")
    search_fields = ("name", "specialty", "email")


@admin.register(AppointmentSlot)
class AppointmentSlotAdmin(admin.ModelAdmin):
    list_display = ("doctor", "date", "slot_index", "is_available", "created_at")
    list_filter = ("is_available", "date", "doctor")
    search_fields = ("doctor__name",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "slot", "status", "created_at", "updated_at")
    list_filter = ("status", "slot__doctor")
    search_fields = ("patient__username", "slot__doctor__name")
