from collections import defaultdict

import pytz
from django.utils import timezone
from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties, ParagraphProperties, TableColumnProperties
from odf.text import P, Span
from odf.table import Table, TableColumn, TableRow, TableCell

from messdiener.models import Mass


def generate_odf_plan_document(plan_pk, file_path):
    # Neues Textdokument erstellen
    document = OpenDocumentText()

    #
    # Styles definieren
    #
    center_bold = Style(name="Center Bold", family="paragraph")
    center_bold.addElement(ParagraphProperties(textalign="center"))
    center_bold.addElement(TextProperties(fontweight="bold"))
    document.styles.addElement(center_bold)

    center = Style(name="Center", family="paragraph")
    center.addElement(ParagraphProperties(textalign="center"))
    document.styles.addElement(center)

    left = Style(name="Left", family="paragraph")
    left.addElement(ParagraphProperties(numberlines="false", linenumber="0", textalign="left"))
    document.styles.addElement(left)

    bold_style = Style(name="Bold", family="text")
    bold_style.addElement(TextProperties(fontweight="bold"))
    document.styles.addElement(bold_style)

    #
    # Breite der Spaleten in den Tabellen setzen
    #
    width_short = Style(name="Wshort", family="table-column")
    width_short.addElement(TableColumnProperties(columnwidth="3.0cm"))
    document.automaticstyles.addElement(width_short)

    width_medium = Style(name="Wmedium", family="table-column")
    width_medium.addElement(TableColumnProperties(columnwidth="4.0cm"))
    document.automaticstyles.addElement(width_medium)

    width_wide = Style(name="Wwide", family="table-column")
    width_wide.addElement(TableColumnProperties(columnwidth="10.59cm"))
    document.automaticstyles.addElement(width_wide)

    # Tabelle mit zwei schmalen und einer breiten Spalte erstellen
    table = Table()
    table.addElement(TableColumn(numbercolumnsrepeated=1, stylename=width_short))
    table.addElement(TableColumn(numbercolumnsrepeated=1, stylename=width_medium))
    table.addElement(TableColumn(numbercolumnsrepeated=1, stylename=width_wide))

    # Generiert eine Zeile in der Tabelle
    def generate_row(datetime, location, extra, acolytes):

        # Datum und Uhrzeit formatieren
        date_string = datetime.strftime("%d.%m.%Y")
        time_string = datetime.strftime("%H:%M")

        # Neue TableRow erstellen und einfügen
        row = TableRow()
        table.addElement(row)

        # Datum - Zeit Zelle anlegen
        date_time_cell = TableCell()
        date_time_cell.addElement(P(stylename=center, text=date_string))
        date_time_cell.addElement(P(stylename=center_bold, text=time_string))

        # Ort - Information Zelle anlegen
        location_extra_cell = TableCell()
        location_extra_cell.addElement(P(stylename=center_bold, text=location))
        location_extra_cell.addElement(P(stylename=center, text=extra))

        # Messdiener Zelle anlegen
        acolytes_cell = TableCell()

        # Messdiener nach Rolle sortiert auflisten
        for role_name in acolytes:
            p = P(stylename=left)
            p.addElement(Span(stylename=bold_style, text=f"{role_name}: "))
            p.addText(text=', '.join(acolytes[role_name]))
            acolytes_cell.addElement(p)

        # Zellen zur TableRow hinzufügen
        row.addElement(date_time_cell)
        row.addElement(location_extra_cell)
        row.addElement(acolytes_cell)

        # TableRow zurückgeben
        return row

    # Durch die Messen nach Zeit sortiert iterieren
    for mass in Mass.objects.filter(plan=plan_pk).order_by('time'):
        # Acolyte dict mit einer leeren Liste als default value anlegen
        acolytes_list = defaultdict(list)

        # Durch die MassAcolyteRoles nach Rolle sortiert iterieren
        for mar in mass.massacolyterole_set.order_by('role__roleName'):
            # Wenn Messdiener keine Rolle hat "Messdiener" als Rolle eintragen
            role = "Messdiener"

            # Wenn Messdiener Rolle hat, dann zur Liste der Messdiener dieser Rolle hinzufügen
            if mar.role is not None:
                role = mar.role.roleName

            # Acolyte Namen setzen. Wenn extra Wert hat, dann in Klammern dahinter setzen
            acolyte_name = f"{mar.acolyte.firstName} {mar.acolyte.lastName}"

            if mar.acolyte.extra:
                acolyte_name = f"{mar.acolyte.firstName} {mar.acolyte.lastName} ({mar.acolyte.extra})"

            acolytes_list[role].append(acolyte_name)

        # Zeit der Messe zur lokalen Zeit konvertieren
        utc = mass.time.replace(tzinfo=pytz.UTC)
        localtime = utc.astimezone(timezone.get_current_timezone())

        # Row generieren und zur Tabelle hinzufügen
        table.addElement(generate_row(
            localtime,
            mass.location.locationName,
            mass.extra,
            acolytes_list
        ))

        # Leere Row für die Übersicht einfügen
        table.addElement(TableRow())

    # Tabelle zum Dokument hinzufügen
    document.text.addElement(table)

    # Dokument speichern
    document.save(file_path)
