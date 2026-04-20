# PikiOra Clinic Booking System

## Project Overview
PikiOra Clinic Booking System is a Django coursework project for managing clinic appointments.
It allows patients to register, log in, browse doctors, view available appointment slots, and book appointments online.
Staff users can access a management dashboard to maintain doctors, slots, appointments, and patient accounts.

## Main Features

### Patient Functions
- Register a patient account
- Log in and log out
- Browse active doctors
- View doctor details and available appointment slots
- Book an appointment
- Edit appointment notes
- Cancel a booked appointment
- View personal appointment records

### Staff Functions
- View dashboard summary data
- Add, edit, and delete doctors
- Add, edit, and delete appointment slots
- View and update appointments
- Cancel appointments from the dashboard
- View and update patient accounts

## Tech Stack
- Python 3.x
- Django 6.0.4
- PostgreSQL
- `python-dotenv`
- `psycopg2-binary`
- Django Template Language
- Custom CSS in `static/css/style.css`

## Project Structure
```text
PikiOra7420/
├── PikiOra7420/          # Project settings and root URL configuration
├── clinic/               # Main clinic application
│   ├── models.py
│   ├── forms.py
│   ├── urls.py
│   ├── views/
│   │   ├── common.py
│   │   ├── user_views.py
│   │   ├── doctor_views.py
│   │   ├── appointment_views.py
│   │   └── management_views.py
│   └── migrations/
├── templates/            # Django templates
├── static/               # Static files
├── manage.py
└── requirements.txt
```

## Database Design
The project mainly uses the following models:

- `Doctor`: stores doctor information such as name, specialty, contact details, and active status
- `AppointmentSlot`: stores available booking slots for each doctor by date and time
- `Appointment`: stores booking records between patients and appointment slots

## User Roles
- `Patient`: can register, log in, browse doctors, and manage personal appointments
- `Staff/Admin`: can access the dashboard and manage clinic data

## Demo Admin Account
For coursework demonstration, the admin account can be used with the following credentials:

- Username: `admin`
- Password: `admin`

## Environment Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment variables
Create a `.env` file in the project root:

```env
PGDATABASE=your_database_name
PGUSER=your_database_user
PGPASSWORD=your_database_password
PGHOST=localhost
```

### 3. Apply migrations
```bash
python manage.py migrate
```

### 4. Create a superuser if needed
```bash
python manage.py createsuperuser
```

### 5. Run the development server
```bash
python manage.py runserver
```

## Main Pages
- Home page: `/`
- Login: `/login/`
- Register: `/register/`
- Patient home: `/patient/home/`
- Doctor list: `/doctors/`
- Slot list: `/slots/`
- My appointments: `/appointments/my/`
- Dashboard: `/dashboard/`

## Suggested Demo Flow
1. Open the home page and show the public entrance.
2. Log in with the admin account and enter the dashboard.
3. Show doctor management, slot management, and appointment management pages.
4. Log out and register a patient account.
5. Browse doctors, view slots, and complete an appointment booking.
6. Open “My Appointments” to edit notes or cancel the booking.

## Notes
- This project is built for coursework submission and demonstration.
- It uses Django built-in authentication and authorization.
- PostgreSQL is configured as the database backend through environment variables.
- The project currently contains only minimal test code and focuses mainly on core functionality.

## Future Improvements
- Add more Django test cases
- Improve validation feedback on forms
- Add more filtering options for appointments and slots
- Further improve the page styling and responsive layout
