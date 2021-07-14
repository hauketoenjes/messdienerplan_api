import itertools
import random
from datetime import date

from django.db import transaction

from messdiener.models import Mass, Acolyte, MassAcolyteRole, Classification


def calculate_age(birthday):
    today = date.today()
    age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
    return age


@transaction.atomic
def generate_plan(plan_pk):
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

        mass_type = mass.type

        # Durch die Anforderungen des Typs iterieren
        for requirement in mass_type.requirements.all():
            role = requirement.role

            # Liste von Einteilungen, die in Frage kommen für den Messetyp
            possible_classifications = list(requirement.classifications.all())

            for _ in itertools.repeat(None, requirement.quantity):
                # Suche den ersten Messdiener, der die Anforderung erfüllt
                selected_acolyte = None

                # TODO Was passiert, wenn es keinen Messdiener in der Altersgruppe gibt? Dann würde das while ewig laufen...
                while selected_acolyte is None:
                    classification_list = list(classification for classification in classification_acolytes_keys if
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
