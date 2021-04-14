from django.contrib import admin

from .models import Coisa
from .models import Temporizadores
from .models import Historico

@admin.register(Coisa)
class CoisaAdmin(admin.ModelAdmin):
    list_display = ( "slug","estato_lampada","ligou_iot_at")

@admin.register(Temporizadores)
class TemporizadoresAdmin(admin.ModelAdmin):
    list_display = ( "coisa","horario","estato","pos")

@admin.register(Historico)
class HistoricoAdmin(admin.ModelAdmin):
    list_display = ( "coisa","dia_mes","tempo_ligado","preço")
