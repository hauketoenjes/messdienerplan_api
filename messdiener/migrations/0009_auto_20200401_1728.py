# Generated by Django 3.0.4 on 2020-04-01 15:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('messdiener', '0008_auto_20200401_0050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requirement',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requirements', to='messdiener.Type'),
        ),
        migrations.AlterField(
            model_name='rule',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rules', to='messdiener.Type'),
        ),
    ]
