# Generated by Django 3.0.4 on 2020-04-15 12:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('messdiener', '0009_auto_20200401_1728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mass',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='messdiener.Location'),
        ),
        migrations.AlterField(
            model_name='requirement',
            name='classifications',
            field=models.ManyToManyField(blank=True, to='messdiener.Classification'),
        ),
    ]
