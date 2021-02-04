import pytz
from django.db import transaction
from django.utils import timezone

from messdiener.models import Mass, Type


@transaction.atomic
def delete_masses_without_type(plan_pk):
    Mass.objects.filter(plan=plan_pk).filter(type__isnull=True).delete()


@transaction.atomic
def assign_types(plan_pk):
    types = Type.objects.all()
    masses = Mass.objects.filter(plan=plan_pk).all()

    for mass in masses:
        for type in types:
            for rule in type.rules.all():
                mass_local_time = convert_to_localtime(mass.time)
                if int_to_day_of_week(mass.time.weekday()) == rule.dayOfWeek \
                        and mass_local_time.hour == rule.time.hour \
                        and mass_local_time.minute == rule.time.minute \
                        and mass.location_id == rule.location_id:
                    mass.type = rule.type
        mass.save()


def int_to_day_of_week(day_int):
    weekday_map = {
        0: "mon",
        1: "tue",
        2: "wed",
        3: "thu",
        4: "fri",
        5: "sat",
        6: "sun",
    }

    return weekday_map[day_int]


def convert_to_localtime(utctime):
    utc = utctime.replace(tzinfo=pytz.UTC)
    localtz = utc.astimezone(timezone.get_current_timezone())
    return localtz
