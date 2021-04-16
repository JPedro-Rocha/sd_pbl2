from django.db import models

#from django.contrib.auth.models import User
from django.urls import reverse


#documentação : https://docs.djangoproject.com/en/3.2/ref/models/fields/#positivebigintegerfield

# Create your models here.
class Coisa(models.Model):
    slug = models.CharField(max_length=100)
    estado_lampada = models.BooleanField( default = False )
    potencia = models.FloatField()
    def __str__(self):
        return self.slug
    def get_absolute_url(self):
        return reverse("IoT:detail",kwargs={"slug":self.slug})
    def get_potencia(self):
        return self.potencia

class Temporizadores( models.Model ):
    horario = models.CharField(max_length=8) # Values from -2147483648 to 2147483647
    estado = models.BooleanField( default = False )
    coisa = models.ForeignKey(Coisa, on_delete=models.CASCADE)
    pos= models.PositiveSmallIntegerField()
    def __str__(self):
        return str(self.horario)
    def get_horario(self):
        return self.horario
        

class Historico( models.Model ):
    date = models.CharField( max_length=11 )
    tempo_ligado = models.PositiveBigIntegerField() #max value 9223372036854775807
    preço = models.FloatField()
    coisa = models.ForeignKey(Coisa, on_delete=models.CASCADE)
    def get_KWh(self):
        return round(((self.tempo_ligado/1000)/3600) * self.coisa.get_potencia(),3 )
    def __str__(self):
        return self.date
    def total(self):
        return round(self.get_KWh() * self.preço,3)