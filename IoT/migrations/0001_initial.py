# Generated by Django 3.1.5 on 2021-04-19 00:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Coisa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.CharField(max_length=100)),
                ('preço', models.FloatField()),
                ('estado_lampada', models.BooleanField(default=False)),
                ('potencia', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Temporizadores',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('horario', models.CharField(max_length=8)),
                ('estado', models.BooleanField(default=False)),
                ('pos', models.PositiveSmallIntegerField()),
                ('coisa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='IoT.coisa')),
            ],
        ),
        migrations.CreateModel(
            name='Historico',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(max_length=11)),
                ('tempo_ligado', models.PositiveBigIntegerField()),
                ('coisa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='IoT.coisa')),
            ],
        ),
    ]
