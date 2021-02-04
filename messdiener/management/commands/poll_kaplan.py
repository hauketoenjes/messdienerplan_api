import csv
import os
from datetime import datetime

from io import StringIO

import pytz
import requests
from django.core.management.base import BaseCommand, CommandError

from messdiener.models import Mass


class Command(BaseCommand):
    help = 'Pollt Kaplan um zu checken, welche Messen ausgefallen sind'

    def handle(self, *args, **options):
        kaplan_base = os.environ['MAPI_KAPLAN_URL']
        kaplan_url = f"{kaplan_base}&days={14}"

        response = requests.get(url=kaplan_url)

        csv_string = StringIO(response.text)

        # read the csv as a dict (ignores the first line and makes it easiert to address the data)
        csv_reader = csv.reader(csv_string, delimiter='\t', lineterminator="\n")

        # iterate through the rows and create the masses
        first_line = True

        masses = Mass.objects.all()

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
            mass_location_string = row[12]

            mass_canceled_string = row[13]
            mass_canceled = False

            if mass_canceled_string != "Falsch":
                mass_canceled = True

            mass = masses.filter(time=mass_date_time, extra=mass_extra,
                                 location__locationName=mass_location_string).first()

            if mass is not None:
                if mass.canceled is not mass_canceled:
                    mass.canceled = mass_canceled
                    mass.save()
                    print("Messe bearbeitet")
