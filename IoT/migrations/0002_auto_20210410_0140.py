# Generated by Django 3.1.5 on 2021-04-10 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('IoT', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='temporizadores',
            name='horario',
            field=models.DateTimeField(),
        ),
    ]
