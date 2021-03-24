import itertools
import random
from datetime import date, timedelta

from django.db import transaction

from messdiener.models import Mass, Acolyte, Group, MassAcolyteRole, Classification


@transaction.atomic
def generate_plan(plan_pk):
    acolytes = Acolyte.objects.filter(inactive=False).all()
    groups = Group.objects.all()

    group_acolyte_classification = {}
    acolyte_classification = {}
    acolyte_classification_index = {}

    # Listen und Maps initialisieren
    for group in groups:
        group_acolyte_classification[group] = {}
        for classification in group.classifications.all():
            group_acolyte_classification[group][classification] = []

    # Die Messdiener den Einteilungen zuordnen
    for acolyte in acolytes:
        age = calculate_age(acolyte.birthday)

        for group in group_acolyte_classification:
            if group != acolyte.group:
                continue

            for classification in group_acolyte_classification[group]:
                if classification.ageFrom <= age <= classification.ageTo:
                    group_acolyte_classification[group][classification].append(acolyte)

    # Die Liste durchmischen um den Plan zufällig zu generieren
    for group in group_acolyte_classification:
        for classification in group_acolyte_classification[group]:
            random.shuffle(group_acolyte_classification[group][classification])
            acolyte_classification[classification] = group_acolyte_classification[group][classification]
            acolyte_classification_index[classification] = 0

    # Falls schon Messdiener eingetragen sind, alle löschen, bei denen der Typ nicht null ist (ohne
    # Typ können keine neuen Messdiener generiert werden)
    MassAcolyteRole.objects.filter(mass__plan_id=plan_pk).filter(mass__type__isnull=False).delete()

    current_mass_time = None
    past_three_days_acolytes = []

    for mass in Mass.objects.filter(plan=plan_pk).order_by('time'):
        if mass.type is None:
            continue

        if current_mass_time is None:
            current_mass_time = mass.time

        if current_mass_time < (mass.time - timedelta(days=3)):
            current_mass_time = mass.time
            past_three_days_acolytes.clear()

        type = mass.type

        for requirement in type.requirements.all():
            role = requirement.role

            for _ in itertools.repeat(None, requirement.quantity):
                acolyte = None
                while acolyte is None or past_three_days_acolytes.__contains__(acolyte):
                    classification = requirement.classifications.order_by('?').first()

                    index = acolyte_classification_index[classification]
                    acolyte_classification_index[classification] = acolyte_classification_index[classification] + 1

                    if index >= len(acolyte_classification[classification]):
                        acolyte_classification_index[classification] = 0
                        index = 0

                    acolyte = acolyte_classification[classification][index]

                past_three_days_acolytes.append(acolyte)
                MassAcolyteRole(mass=mass, acolyte=acolyte, role=role).save()


def calculate_age(birthday):
    today = date.today()
    age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
    return age


def generate_plan_refactor(plan_pk):
    acolytes = Acolyte.objects.filter(inactive=False).all()
    classifications = Classification.objects.all()

    # acolyte_availability = {acolyte, bool}
    # classification_acolytes = {classification, [acolyte, ...]}
    acolyte_availability = {}
    classification_acolytes = {}

    shuffled_acolytes = list(acolytes)
    random.shuffle(shuffled_acolytes)

    # classification_acolytes dict mit leeren Listen initialisieren
    for classification in classifications:
        classification_acolytes[classification] = []

    # Durch alle Messdiener iterieren und mit Alters- und Verfügbarkeitsinformationen in einem Dict speichern
    for acolyte in shuffled_acolytes:
        # Alle Messdiener initial auf Verfügbar setzten
        acolyte_availability[acolyte] = True

        # Alter berechnen
        age = calculate_age(acolyte.birthday)

        # Durch die Einteilungen des jeweiligen Messdieners iterieren, wenn die Gruppe stimmt
        for classification in (classification for classification in classifications if
                               classification.group == acolyte.group):

            # Alter überprüfen und classifcation hinzufügen, falls im Bereich
            if classification.ageFrom <= age <= classification.ageTo:
                classification_acolytes[classification].append(acolyte)

    # Einteilungen mischen
    classification_acolytes_keys = [*classification_acolytes]
    random.shuffle(classification_acolytes_keys)

    # Falls schon Messdiener eingetragen sind, alle löschen, bei denen der Typ nicht null ist (ohne
    # Typ können keine neuen Messdiener generiert werden)
    MassAcolyteRole.objects.filter(mass__plan_id=plan_pk).filter(mass__type__isnull=False).delete()

    # Durch die Messen nach Zeit sortiert iterieren um den größtmöglichen Abstand zwischen zwei Einteilungen zu sichern
    for mass in Mass.objects.filter(plan=plan_pk).order_by('time'):
        # Wenn der Messetyp None ist überspringen, weil keine neuen Messdiener generiert werden können
        if mass.type is None:
            continue

        type = mass.type

        # Durch die Anforderungen des Typs iterieren
        for requirement in type.requirements.all():
            role = requirement.role

            # Liste von Einteilungen, die in Frage kommen für den Messetyp
            possible_classifications = list(requirement.classifications.all())

            for _ in itertools.repeat(None, requirement.quantity):
                # Suche den ersten Messdiener, der die Anforderung erfüllt
                selected_acolyte = None

                # TODO Was passiert, wenn es keinen Messdiener in der Altersgruppe gibt? Dann würde das while ewig laufen...
                while selected_acolyte is None:
                    classification_list = (classification for classification in classification_acolytes_keys if
                                           classification in possible_classifications)

                    for classification in classification_list:

                        for acolyte in classification_acolytes[classification]:
                            if acolyte_availability[acolyte]:
                                acolyte_availability[acolyte] = False
                                selected_acolyte = acolyte
                                break

                        # Falls schon ein Messdiener gefunden wurde, breaken um nicht weiter zu suchen
                        if selected_acolyte is not None:
                            break

                    # Wenn kein Messdiener in gefunden wurde, setzte alle Messdiener in den Altersgruppen wieder auf
                    # Verfügbar
                    if selected_acolyte is None:
                        for classification in classification_list:
                            for acolyte in classification_acolytes[classification]:
                                acolyte_availability[acolyte] = True

                MassAcolyteRole(mass=mass, acolyte=selected_acolyte, role=role).save()
