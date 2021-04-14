from django.db import models

#from django.contrib.auth.models import User
from django.urls import reverse


#documentação : https://docs.djangoproject.com/en/3.2/ref/models/fields/#positivebigintegerfield

# Create your models here.
class Coisa(models.Model):
    slug = models.CharField(max_length=100)
    estato_lampada = models.BooleanField( default = False )
    ligou_iot_at = models.DateTimeField(auto_now=True)# A date and time, represented in Python by a datetime.datetime instance.
    def __str__(self):
        return self.slug
    def get_absolute_url(self):
        return reverse("IoT:detail",kwargs={"slug":self.slug})

class Temporizadores( models.Model ):
    horario = models.IntegerField(  ) # Values from -2147483648 to 2147483647
    estato = models.BooleanField( default = True )
    coisa = models.ForeignKey(Coisa, on_delete=models.CASCADE)
    pos= models.PositiveSmallIntegerField()
    def __str__(self):
        c = self.horario/60000
        return f'{int(c/60)}:{int(c%60)}'

    def get_horario(self):
        c = self.horario/60000
        return   f'{int(c/60):02}:{int(c%60):02}'
        

class Historico( models.Model ):
    dia_mes = models.CharField( max_length=6 )
    tempo_ligado = models.PositiveBigIntegerField() #max value 9223372036854775807
    preço = models.FloatField()
    coisa = models.ForeignKey(Coisa, on_delete=models.CASCADE)
    def __str__(self):
        return self.mes_ano