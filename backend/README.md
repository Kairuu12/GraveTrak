# GraveTrak Django Backend

This backend is built with Django and Django REST Framework. It exposes a simple REST API for graves and user authentication.

## Setup

1. Create a Python virtual environment in `backend`.
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```powershell
   python manage.py migrate
   ```
4. Start the server:
   ```powershell
   python manage.py runserver
   ```

## Demo Accounts

- Admin: `admin@lgu.gov.ph` / `adminpass`
- Mayor: `mayor@lgu.gov.ph` / `mayorpass`
- Planning: `planner@lgu.gov.ph` / `planningpass`
- Public User: `user@lgu.gov.ph` / `userpass`

## API Endpoints

- `POST /api/login/`
- `POST /api/register/`
- `POST /api/logout/`
- `GET /api/profile/`
- `GET /api/graves/`
- `POST /api/graves/`
- `PATCH /api/graves/{id}/`
- `DELETE /api/graves/{id}/`
- `GET /api/users/` (staff/admin only)
