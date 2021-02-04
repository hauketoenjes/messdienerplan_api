from rest_framework import serializers
from .models import *


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'locationName')


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'roleName')


class ClassificationSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        group = Group.objects.get(pk=self.context['view'].kwargs['group_pk'])
        validated_data['group'] = group
        return Classification.objects.create(**validated_data)

    class Meta:
        model = Classification
        fields = ('id', 'ageFrom', 'ageTo')


class GroupSerializer(serializers.ModelSerializer):
    classifications = ClassificationSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ('id', 'groupName', 'classifications')


class RequirementSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        type = Type.objects.get(pk=self.context['view'].kwargs['type_pk'])

        requirement = Requirement.objects.create(type=type, quantity=validated_data['quantity'],
                                                 role=validated_data['role'])

        requirement.classifications.set(validated_data['classifications'])
        return requirement

    class Meta:
        model = Requirement
        fields = ('id', 'quantity', 'role', 'classifications')


class RuleSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        type = Type.objects.get(pk=self.context['view'].kwargs['type_pk'])
        validated_data['type'] = type
        return Rule.objects.create(**validated_data)

    class Meta:
        model = Rule
        fields = ('id', 'location', 'time', 'dayOfWeek')


class TypeSerializer(serializers.ModelSerializer):
    requirements = RequirementSerializer(many=True, read_only=True)
    rules = RuleSerializer(many=True, read_only=True)

    class Meta:
        model = Type
        fields = ('id', 'typeName', 'requirements', 'rules')


class AcolyteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acolyte
        fields = ('id', 'firstName', 'lastName', 'extra', 'birthday', 'group', 'inactive')


class CreateRequirementClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classification
        fields = ('id',)


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ('id', 'dateFrom', 'dateTo', 'public')


class MassSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        plan = Plan.objects.get(pk=self.context['view'].kwargs['plan_pk'])
        validated_data['plan'] = plan
        return Mass.objects.create(**validated_data)

    class Meta:
        model = Mass
        fields = ('id', 'time', 'extra', 'location', 'type', 'canceled')


class AcolyteMassSerializer(serializers.ModelSerializer):
    class Meta:
        model = MassAcolyteRole
        fields = ('id', 'mass', 'role')


class MassAcolyteSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        mass = Mass.objects.get(pk=self.context['view'].kwargs['mass_pk'])
        validated_data['mass'] = mass
        return MassAcolyteRole.objects.create(**validated_data)

    class Meta:
        model = MassAcolyteRole
        fields = ('id', 'acolyte', 'role')
        write_only_fields = ('mass',)


class CurrentPlanAcolyteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acolyte
        fields = ('firstName', 'lastName', 'extra',)


class AcolyteRoleSerializer(serializers.ModelSerializer):
    role = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='roleName'
    )
    acolyte = CurrentPlanAcolyteSerializer(many=False)

    class Meta:
        model = MassAcolyteRole
        fields = ('role', 'acolyte')


class CurrentPlanSerializer(serializers.ModelSerializer):
    acolytes = serializers.SerializerMethodField()
    location = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='locationName'
    )

    class Meta:
        model = Mass
        fields = ('time', 'extra', 'location', 'canceled', 'acolytes')

    def get_acolytes(self, obj):
        queryset = MassAcolyteRole.objects.filter(mass=obj)
        return AcolyteRoleSerializer(queryset, many=True).data
