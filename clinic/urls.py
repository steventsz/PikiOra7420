from django.urls import path

from . import views

app_name = "clinic"

urlpatterns = [
    path("", views.DoctorListView.as_view(), name="doctor_list"),
    path("doctors/<int:pk>/", views.DoctorDetailView.as_view(), name="doctor_detail"),
    path("slots/<int:slot_id>/book/", views.book_appointment, name="book_appointment"),
    path("appointments/", views.my_appointments, name="my_appointments"),
    path(
        "appointments/<int:pk>/cancel/",
        views.cancel_appointment,
        name="cancel_appointment",
    ),
]
