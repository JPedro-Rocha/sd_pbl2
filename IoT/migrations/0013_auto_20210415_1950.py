# Generated by Django 3.1.5 on 2021-04-15 22:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('IoT', '0012_auto_20210415_1944'),
    ]

    operations = [
        migrations.RenameField(
            model_name='coisa',
            old_name='estato_lampada',
            new_name='estado_lampada',
        ),
        migrations.RenameField(
            model_name='temporizadores',
            old_name='estato',
            new_name='estado',
        ),
    ]
