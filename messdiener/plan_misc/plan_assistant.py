import os
from io import StringIO

import pytz
import requests
import csv
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist, SuspiciousOperation
from django.db import transaction
from django.db.utils import IntegrityError

from messdiener.models import Plan, Location, Mass


@transaction.atomic
def create_import_plan(date_from, date_to):
    # convert the date strings to datetime objects
    plan_start = datetime.strptime(date_from, "%Y-%m-%d")
    plan_end = datetime.strptime(date_to, "%Y-%m-%d")

    # create a new plan
    plan = Plan(dateFrom=plan_start.date(), dateTo=plan_end.date())
    plan.save()

    # calculate the days to fetch (only future dates can be fetched from the server)
    days_to_fetch = (plan_end - datetime.now()).days + 4

    kaplan_base = os.environ['MAPI_KAPLAN_URL']
    kaplan_url = f"{kaplan_base}&days={days_to_fetch}"

    response = requests.get(url=kaplan_url)

    csv_string = StringIO(response.text)

    # read the csv as a dict (ignores the first line and makes it easiert to address the data)
    csv_reader = csv.reader(csv_string, delimiter='\t', lineterminator="\n")

    # iterate through the rows and create the masses
    first_line = True

    for row in csv_reader:
        if first_line:
            first_line = False
            continue

        # datetime of mass
        mass_date = datetime.strptime(row[1], "%d.%m.%Y")
        mass_date_time = datetime(mass_date.year, mass_date.month, mass_date.day, int(row[2]), int(row[3]))

        # convert datetime of
        mass_date_time = pytz.timezone('CET').localize(mass_date_time)

        mass_extra = row[6]
        mass_location_string = row[13]

        try:
            with transaction.atomic():
                # get the location object
                mass_location = Location.objects.get(locationName=mass_location_string)

                # insert mass into the database
                Mass(plan=plan, time=mass_date_time, extra=mass_extra, location=mass_location).save()

        except (ObjectDoesNotExist, SuspiciousOperation, IntegrityError):
            # if the mass is not in range of the parent plan or the location does not exist, skip it
            continue

    return plan
