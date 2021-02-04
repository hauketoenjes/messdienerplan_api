from django.core.exceptions import SuspiciousOperation
from django.db import models

from django.db.models import Q


class Location(models.Model):
    locationName = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.locationName


class Role(models.Model):
    roleName = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.roleName


class Group(models.Model):
    groupName = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.groupName


class Type(models.Model):
    typeName = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.typeName


class Classification(models.Model):
    ageFrom = models.IntegerField()
    ageTo = models.IntegerField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="classifications")

    def __str__(self):
        return '%s (%d - %d)' % (self.group.groupName, self.ageFrom, self.ageTo)

    class Meta:
        unique_together = ('ageFrom', 'ageTo', 'group')


class Requirement(models.Model):
    quantity = models.IntegerField()
    role = models.ForeignKey(Role, on_delete=models.CASCADE, blank=True, null=True)
    type = models.ForeignKey(Type, on_delete=models.CASCADE, related_name='requirements')
    classifications = models.ManyToManyField(Classification, blank=True)

    def __str__(self):
        return '%d %s' % (self.quantity, self.role)

    class Meta:
        unique_together = ('quantity', 'role', 'type')


class Rule(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    time = models.TimeField()
    type = models.ForeignKey(Type, on_delete=models.CASCADE, related_name='rules')
    dayOfWeek = models.CharField(choices=(
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', ' Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ), max_length=3)

    class Meta:
        unique_together = ('location', 'time', 'type', 'dayOfWeek')


class Acolyte(models.Model):
    firstName = models.CharField(max_length=200)
    lastName = models.CharField(max_length=200)
    extra = models.CharField(max_length=200, blank=True)
    birthday = models.DateField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)
    inactive = models.BooleanField(default=False)

    def __str__(self):
        return '%s %s' % (self.firstName, self.lastName)

    class Meta:
        unique_together = ('firstName', 'lastName', 'extra', 'birthday')


class Plan(models.Model):
    dateFrom = models.DateField()
    dateTo = models.DateField()
    public = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        try:
            plan = Plan.objects.get(Q(dateFrom__range=(self.dateFrom, self.dateTo)) | Q(
                dateTo__range=(self.dateFrom, self.dateTo)) | Q(dateFrom__lte=self.dateFrom,
                                                                dateTo__gte=self.dateTo)
                                    )
            if self.id != plan.id:
                raise SuspiciousOperation("Overlapping dates")
            else:
                super(Plan, self).save(*args, **kwargs)
        except Plan.DoesNotExist:
            super(Plan, self).save(*args, **kwargs)


class Mass(models.Model):
    time = models.DateTimeField()
    extra = models.CharField(max_length=200, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    type = models.ForeignKey(Type, on_delete=models.CASCADE, blank=True, null=True)
    acolytes = models.ManyToManyField(Acolyte, through='MassAcolyteRole')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='masses')
    canceled = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.time.date() < self.plan.dateFrom or self.time.date() > self.plan.dateTo:
            raise SuspiciousOperation("Mass is not in range of plan")
        else:
            super(Mass, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('time', 'extra', 'location')


class MassAcolyteRole(models.Model):
    acolyte = models.ForeignKey(Acolyte, on_delete=models.CASCADE)
    mass = models.ForeignKey(Mass, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ('acolyte', 'mass')
