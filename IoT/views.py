from django.shortcuts import render

from django.views.generic import DetailView,ListView
from .models import *
from django.template import loader
from django.http import HttpResponse

class CoisaListView(ListView):
    model=Coisa

class CoisaDetailView(DetailView):
    model=Coisa
    def get_context_data(self, *args, **kwargs):
        context = super(CoisaDetailView,
             self).get_context_data(*args, **kwargs) 
        context["temporizadores"] = Temporizadores.objects.filter(coisa=context["coisa"])
        return context

class CoisaDetailView_add(CoisaDetailView):
    def get_context_data(self, *args, **kwargs):
        context = super(CoisaDetailView,
             self).get_context_data(*args, **kwargs) 
        context["temporizadores"] = Temporizadores.objects.filter(coisa=context["coisa"])
        def add_temporizador():
            if(len(context["temporizadores"]) < 10):
                t = Temporizadores(coisa=context["coisa"], estato=False, horario=0, pos=len(context["temporizadores"]))
                t.save()
        context["add_temporizador"] = add_temporizador
        return context

def remov_temp(request,slug,poss):
    coisa = Coisa.objects.get(slug=slug)
    template = loader.get_template("IoT/coisa_detail.html")
    t = Temporizadores.objects.filter(coisa=coisa).filter(pos=poss)
    t.delete()
    temporizadores = Temporizadores.objects.filter(coisa=coisa)
    context={
        "coisa":coisa,
        "temporizadores":temporizadores
    }
    return HttpResponse(template.render(context,request))

def add_temp(request,slug):
    if(request.method == "GET"):
        coisa = Coisa.objects.get(slug=slug)
        template = loader.get_template("IoT/coisa_detail.html")
        temporizadores = Temporizadores.objects.filter(coisa=coisa)
        a = [False for t in range(10)]
        for t in temporizadores:
            a[t.pos] = True
        for n,b in enumerate(a):
            if(not(b)):
                pos=n
                break
        try:
            t = Temporizadores(coisa=coisa, estato=False, horario=0, pos=pos)
            t.save()
        except:
            pass
        temporizadores = Temporizadores.objects.filter(coisa=coisa)
        context={
            "coisa":coisa,
            "temporizadores":temporizadores
        }
        return HttpResponse(template.render(context,request))

def atualizar_temporizador(request,pos):
    print()
    print()
    print(request)
    return CoisaDetailView_add.as_view()
