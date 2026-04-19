from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "clinic"

urlpatterns = [
    # Public and user pages
    path("", views.HomeView.as_view(), name="home"),
    path(
        "login/",
        views.RoleBasedLoginView.as_view(),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", views.PatientRegisterView.as_view(), name="register"),
    path("patient/home/", views.PatientHomeView.as_view(), name="patient_home"),

    # Doctor pages
    path("doctors/", views.DoctorListView.as_view(), name="doctor_list"),
    path("doctors/<int:pk>/", views.DoctorDetailView.as_view(), name="doctor_detail"),
    path("slots/", views.SlotListView.as_view(), name="slot_list"),

    # Appointment pages
    path(
        "appointments/book/<int:slot_id>/",
        views.BookAppointmentView.as_view(),
        name="book_appointment",
    ),
    path("appointments/my/", views.MyAppointmentsView.as_view(), name="my_appointments"),
    path(
        "appointments/<int:pk>/edit/",
        views.EditAppointmentView.as_view(),
        name="edit_appointment",
    ),
    path(
        "appointments/<int:pk>/cancel/",
        views.CancelAppointmentView.as_view(),
        name="cancel_appointment",
    ),

    # Dashboard pages
    path("dashboard/", views.DashboardHomeView.as_view(), name="dashboard_home"),
    path(
        "dashboard/doctors/",
        views.DashboardDoctorListView.as_view(),
        name="dashboard_doctor_list",
    ),
    path(
        "dashboard/doctors/add/",
        views.DashboardDoctorCreateView.as_view(),
        name="dashboard_doctor_add",
    ),
    path(
        "dashboard/doctors/<int:pk>/edit/",
        views.DashboardDoctorUpdateView.as_view(),
        name="dashboard_doctor_edit",
    ),
    path(
        "dashboard/doctors/<int:pk>/delete/",
        views.DashboardDoctorDeleteView.as_view(),
        name="dashboard_doctor_delete",
    ),
    path(
        "dashboard/slots/",
        views.DashboardSlotListView.as_view(),
        name="dashboard_slot_list",
    ),
    path(
        "dashboard/slots/add/",
        views.DashboardSlotCreateView.as_view(),
        name="dashboard_slot_add",
    ),
    path(
        "dashboard/slots/<int:pk>/edit/",
        views.DashboardSlotUpdateView.as_view(),
        name="dashboard_slot_edit",
    ),
    path(
        "dashboard/slots/<int:pk>/delete/",
        views.DashboardSlotDeleteView.as_view(),
        name="dashboard_slot_delete",
    ),
    path(
        "dashboard/appointments/",
        views.DashboardAppointmentListView.as_view(),
        name="dashboard_appointment_list",
    ),
    path(
        "dashboard/appointments/<int:pk>/edit/",
        views.DashboardAppointmentUpdateView.as_view(),
        name="dashboard_appointment_edit",
    ),
    path(
        "dashboard/appointments/<int:pk>/cancel/",
        views.DashboardAppointmentCancelView.as_view(),
        name="dashboard_appointment_cancel",
    ),
    path(
        "dashboard/patients/",
        views.DashboardPatientListView.as_view(),
        name="dashboard_patient_list",
    ),
    path(
        "dashboard/patients/<int:pk>/edit/",
        views.DashboardPatientUpdateView.as_view(),
        name="dashboard_patient_edit",
    ),
]
