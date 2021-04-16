from django.contrib import admin

from .models import Coisa
from .models import Temporizadores
from .models import Historico

@admin.register(Coisa)
class CoisaAdmin(admin.ModelAdmin):
    list_display = ( "slug","estado_lampada","potencia")

@admin.register(Temporizadores)
class TemporizadoresAdmin(admin.ModelAdmin):
    list_display = ( "coisa","horario","estado","pos")

@admin.register(Historico)
class HistoricoAdmin(admin.ModelAdmin):
    list_display = ( "coisa","date","tempo_ligado","preço")
