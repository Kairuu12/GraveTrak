import sys
from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError

# --- BUG FIX PARA SA PYTHON 3.14 & DJANGO 4.2 ---
import copy
from django.template.context import BaseContext, Context

def patched_basecontext_copy(self):
    duplicate = type(self).__new__(type(self))
    duplicate.__dict__.update(self.__dict__)
    duplicate.dicts = self.dicts[:]
    return duplicate

def patched_context_copy(self):
    duplicate = patched_basecontext_copy(self)
    if hasattr(self, 'render_context'):
        duplicate.render_context = copy.copy(self.render_context)
    return duplicate

BaseContext.__copy__ = patched_basecontext_copy
Context.__copy__ = patched_context_copy
# -------------------------------------------------

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        if any(arg in sys.argv for arg in ['makemigrations', 'migrate', 'collectstatic', 'test']):
            return

        try:
            from django.contrib.auth import get_user_model
            from .models import UserProfile, ColumbariumSlot
            User = get_user_model()

            # Seed Mayor's Office Superuser
            if not User.objects.filter(username='officeofmayors').exists():
                mayor_user = User.objects.create_superuser(
                    username='officeofmayors',
                    email='cmayor@gmail.com',
                    password='mayorsoffice',
                    first_name='Office of',
                    last_name='Mayors',
                )
                UserProfile.objects.update_or_create(user=mayor_user, defaults={'role': 'mayor'})

            # CPDO and Cemetery Staff are business roles, not Django superusers.
            if not User.objects.filter(username='cpdo').exists():
                planner_user = User.objects.create_user(
                    username='cpdo',
                    email='cplanning@gmail.com',
                    password='cityplanning',
                    first_name='City',
                    last_name='Planner',
                )
                UserProfile.objects.update_or_create(user=planner_user, defaults={'role': 'planning'})

            # Seed Cemetery Staff
            if not User.objects.filter(username='cemetery_staff').exists():
                admin_user = User.objects.create_user(
                    username='cemetery_staff',
                    email='cstaff@gmail.com',
                    password='cemeterystaff',
                    first_name='Cemetery',
                    last_name='Staff',
                )
                UserProfile.objects.update_or_create(user=admin_user, defaults={'role': 'staff'})

            # Only seed default columbarium slots when the table is empty.
            # This prevents overwriting real data on each server start.
            if not ColumbariumSlot.objects.exists():
                target_columbarium_sections = [f'Section {letter}' for letter in 'ABCDEFGHIJKLMN']
                target_columbarium_floors = [1, 2, 3, 4]
                target_columbarium_cols = list(range(1, 85))

                columbarium_slots = []
                for sec in target_columbarium_sections:
                    for f in target_columbarium_floors:
                        for c in target_columbarium_cols:
                            slot_id = f'{sec}-old-F{f}-C{c}'
                            columbarium_slots.append(ColumbariumSlot(
                                id=slot_id,
                                section=sec,
                                floor=f,
                                col=c,
                                cemetery_map='old',
                                status='available',
                                name='',
                            ))

                new_columbarium_sections = ['Section A', 'Section B']
                new_columbarium_floors = [1, 2, 3, 4]
                new_columbarium_cols = list(range(1, 133))

                for sec in new_columbarium_sections:
                    for f in new_columbarium_floors:
                        for c in new_columbarium_cols:
                            slot_id = f'{sec}-new-F{f}-C{c}'
                            columbarium_slots.append(ColumbariumSlot(
                                id=slot_id,
                                section=sec,
                                floor=f,
                                col=c,
                                cemetery_map='new',
                                status='available',
                                name='',
                            ))

                for i in range(0, len(columbarium_slots), 1000):
                    ColumbariumSlot.objects.bulk_create(columbarium_slots[i:i+1000], batch_size=1000)

            from .models import Application
            sample_applications = [
                {'id': 'BUR-DEMO-001', 'name': 'Sample Burial', 'applicant': 'Test User', 'submitted': 'May 2026', 'status': 'Review'},
            ]
            for app_data in sample_applications:
                Application.objects.get_or_create(id=app_data['id'], defaults=app_data)
        except (OperationalError, ProgrammingError):
            return
