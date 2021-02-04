import tempfile
from datetime import date

from django.http import FileResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from messdiener.plan_misc.plan_assistant import create_import_plan
from messdiener.plan_misc.plan_generator import generate_plan_refactor
from messdiener.plan_misc.plan_odt_generator import generate_odf_plan_document
from messdiener.plan_misc.plan_utils import delete_masses_without_type, assign_types
from .serializers import *


class LocationView(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class RoleView(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class ClassificationView(viewsets.ModelViewSet):
    serializer_class = ClassificationSerializer

    def get_queryset(self):
        return Classification.objects.filter(group=self.kwargs['group_pk'])


class GroupView(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class TypeView(viewsets.ModelViewSet):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer


class RequirementView(viewsets.ModelViewSet):
    serializer_class = RequirementSerializer

    def get_queryset(self):
        return Requirement.objects.filter(type=self.kwargs['type_pk'])


class RuleView(viewsets.ModelViewSet):
    serializer_class = RuleSerializer

    def get_queryset(self):
        return Rule.objects.filter(type=self.kwargs['type_pk'])


class AcolyteView(viewsets.ModelViewSet):
    queryset = Acolyte.objects.all()
    serializer_class = AcolyteSerializer


class MassView(viewsets.ModelViewSet):
    serializer_class = MassSerializer

    def get_queryset(self):
        return Mass.objects.filter(plan=self.kwargs['plan_pk'])


class MassAcolyteView(viewsets.ModelViewSet):
    serializer_class = MassAcolyteSerializer

    def get_queryset(self):
        return MassAcolyteRole.objects.filter(mass=self.kwargs['mass_pk'])


class AcolyteMassView(viewsets.ReadOnlyModelViewSet):
    serializer_class = AcolyteMassSerializer

    def get_queryset(self):
        return MassAcolyteRole.objects.filter(acolyte=self.kwargs['acolyte_pk'])


class PlanView(viewsets.ModelViewSet):
    serializer_class = PlanSerializer

    queryset = Plan.objects.all()

    # Action to generate a specific plan
    @action(detail=True, methods=['get'])
    def generate_odf_document(self, request, pk=None):
        # Temporären Ordner erstellen (wird gelöscht, wenn der Context verlassen wird)
        with tempfile.TemporaryDirectory() as tmpdirname:
            plan = self.get_object()

            # Dateinamen auf "Messdienerplan_DatumVon-DatumBis.odt" setzen
            file_name = f'Messdienerplan_{plan.dateFrom.strftime("%d_%m_%Y")}-{plan.dateTo.strftime("%d_%m_%Y")}.odt'

            # Dateipfad in Temporären Ordner legen
            file_path = f"{tmpdirname}/{file_name}.odt"

            # Dokument generieren und im temporären Ordner speichern
            generate_odf_plan_document(pk, file_path)

            # Temporäre Datei öffnen als bytestream
            file = open(file_path, 'r+b')

            # Datei als FileResponse mit odt-text als MimeType schicken
            response = FileResponse(file, content_type=u'application/vnd.oasis.opendocument.text')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'

            return response

    # Action um den Messdienerplan zu generieren
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        generate_plan_refactor(pk)
        return Response()

    # Action um die Messen ohne Typ zu löschen
    @action(detail=True, methods=['post'])
    def delete_masses_without_type(self, request, pk=None):
        delete_masses_without_type(pk)
        return Response()

    # Action um die Messetypen automatisch den Messen zuzuordnen
    @action(detail=True, methods=['post'])
    def assign_types(self, request, pk=None):
        assign_types(pk)
        return Response()

    # Action um einen Plan von KaPlan automatisch zu importieren und
    @action(detail=False, methods=['post'])
    def create_import_plan(self, request):
        plan = create_import_plan(request.data['dateFrom'], request.data['dateTo'])
        serializer = PlanSerializer(plan)
        return Response(serializer.data)


class CurrentPlanView(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        now = date.today()

        # Get all masses, where the plan end date is in the future (current and future plans) and only plans
        # which are public
        queryset = Mass.objects.all().filter(plan__dateTo__gte=now).filter(plan__public=True)
        serializer = CurrentPlanSerializer(queryset, many=True)
        return Response(serializer.data)
