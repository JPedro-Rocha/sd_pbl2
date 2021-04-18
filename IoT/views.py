from django.shortcuts import render

from django.views.generic import DetailView,ListView
from .models import *
from django.template import loader
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime,timedelta
from IoT import MQTT

class CoisaListView(ListView):
    model=Coisa

def listar(request):
    coisas = Coisa.objects.all()
    template = loader.get_template("IoT/coisa_list.html")
    vet = []
    for c in coisas:
        vet.append( MQTT.confirma_coisa(c.slug) )
    context = {"coisa_list":zip(coisas,vet)}
    return HttpResponse(template.render(context,request))

def coisa(request, slug):
    if(MQTT.confirma_coisa(slug)):
        template = loader.get_template("IoT/coisa_detail.html")
        context = __get_base_context(slug)
        return HttpResponse(template.render(context,request))
    else:
        template = loader.get_template("IoT/offline.html")
        context={"slug":slug}
        return HttpResponse(template.render(context,request))
    
def remov_temp(request,slug,poss):
    if(MQTT.confirma_coisa(slug)):
        coisa = Coisa.objects.get(slug=slug)
        template = loader.get_template("IoT/coisa_detail.html")
        t = Temporizadores.objects.filter(coisa=coisa).filter(pos=poss)
        t = t[0]
        msg = {
            "tempo":t.horario,
            "estado":1 if(t.estado) else 0,
            "posição":poss,
            "is_add":0,
            "should_be_trigger":0 }
        MQTT.publish(f"{slug}/temporizador",msg)
        t.delete()
        context = __get_base_context(slug)
        return HttpResponse(template.render(context,request))
    else:
        template = loader.get_template("IoT/offline.html")
        context={"slug":slug}
        return HttpResponse(template.render(context,request))

def add_temp(request,slug):
    if(MQTT.confirma_coisa(slug)):
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
            if(pos < 10):
                t = Temporizadores(coisa=coisa, estado=False, horario="00:00:02", pos=pos)
                msg = { "tempo":t.horario,
                    "estado": 1 if(t.estado) else 0,
                    "posição":t.pos,
                    "is_add": 1,
                    "should_be_trigger": 1 }
                MQTT.publish(f'{slug}/temporizador',msg)
                t.save()
        except:
            pass
        context = __get_base_context(slug)
        return HttpResponse(template.render(context,request))
    else:
        template = loader.get_template("IoT/offline.html")
        context={"slug":slug}
        return HttpResponse(template.render(context,request))

def atualizar_temporizador(request,slug,pos):
    if(MQTT.confirma_coisa(slug)):
        coisa = Coisa.objects.get(slug=slug)
        temporizadores = Temporizadores.objects.filter(coisa=coisa)
        template = loader.get_template("IoT/coisa_detail.html")
        if(request.method == "POST"):
            temporizadores = temporizadores.filter(pos=pos)
            for t in temporizadores:
                pass
            t.horario = request.POST.get("horario")
            t.estado = request.POST.get("estado") == "on"

            now = datetime.now()
            dt_string = now.strftime("%H:%M:%S")
            msg = { "tempo":t.horario,
                        "estado": 1 if(t.estado) else 0,
                        "posição":t.pos,
                        "is_add": 1,
                        "should_be_trigger": 1 if (t.horario >= dt_string) else 0 }
            MQTT.publish(f'{slug}/temporizador',msg)
            t.save()
        context = __get_base_context(slug)
        return HttpResponse(template.render(context,request))
    else:
        template = loader.get_template("IoT/offline.html")
        context={"slug":slug}
        return HttpResponse(template.render(context,request))

def set_timer(request,slug):
    if(MQTT.confirma_coisa(slug)):
        template = loader.get_template("IoT/coisa_detail.html")
        if(request.method == "POST"):
            print(request.POST)
            msg = {}
            now = datetime.now()
            if(request.POST.get("timer_on") != None):
                msg["is_ligado"] = 1 if(request.POST.get("timer_on") == "on") else 0
            else:
                msg["is_ligado"]=1
            if( msg["is_ligado"] == 1):
                s = request.POST.get("tempo")
                s = s.split(":")
                s = timedelta( seconds=int(s[2]), minutes=int(s[1]),hours=int(s[0]))
                s = now + s
            now_string = s.strftime("%H:%M:%S")
            msg["set_timer"] = now_string
            print(msg)
            MQTT.publish(f"{slug}/set_timer", msg)
            MQTT.coisas[slug]["estado_timer"] = (["is_ligado"]==1)
            MQTT.coisas[slug]["timer"] = msg["set_timer"] if(MQTT.coisas[slug]["estado_timer"]) else "00:00:00"
        context = __get_base_context(slug)
        return HttpResponse(template.render(context,request))
    else:
        template = loader.get_template("IoT/offline.html")
        context={"slug":slug}
        return HttpResponse(template.render(context,request))


@csrf_exempt
def altera_lamp(request, slug):
    if(MQTT.confirma_coisa(slug)):
        coisa = Coisa.objects.get(slug=slug)
        template = loader.get_template("IoT/coisa_detail.html")
        if(request.method == "POST"):
            coisa.estado_lampada = (request.POST.get("lampada") == "true")
            coisa.save()
            msg = {"novo_estado": 1 if(coisa.estado_lampada) else 0 }
            MQTT.publish(f"{slug}/OnOff", msg)
        context = __get_base_context(slug)
        return HttpResponse(template.render(context,request))
    else:
        template = loader.get_template("IoT/offline.html")
        context={"slug":slug}
        return HttpResponse(template.render(context,request))

#
def __get_base_context(slug):
    for a in range(10000000):
        pass
    coisa = Coisa.objects.get(slug=slug)
    temporizadores = Temporizadores.objects.filter(coisa=coisa)
    context={               
        "coisa":coisa,
        "temporizadores":temporizadores
    }
    context["historico"] = Historico.objects.filter(coisa=context["coisa"])[::-1][:30]
    try:
        for a in range(1000000):
            if(MQTT.coisas[slug]["timer"] != None and MQTT.coisas[slug]["estado_timer"] !=None ):
                context["timer"] = MQTT.coisas[slug]["timer"]
                context["estado_timer"] = MQTT.coisas[slug]["estado_timer"]
                break
#        print(MQTT.coisas[slug]["timer"],MQTT.coisas[slug]["estado_timer"])
    except:
#        print("Sem timer")
        pass
    return context