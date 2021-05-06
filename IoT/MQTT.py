import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
from .models import *
import json
from datetime import date


client = AWSIoTPyMQTT.AWSIoTMQTTClient("meu_client")
#C:\\Users\\dfc15\\Desktop\\materias\\SD\\Problema-2\\site_pbl_2\\sd_pbl2\\IoT\\certificates\\
#/home/ubuntu/sd_pbl2/IoT/
client.configureEndpoint("at9zi9dd4t3sg-ats.iot.us-east-1.amazonaws.com", 8883)
client.configureCredentials("/home/ubuntu/sd_pbl2/IoT/certificates/AmazonRootCA1.pem", 
                            "/home/ubuntu/sd_pbl2/IoT/certificates/a504e91ba6-private.pem.key",
                            "/home/ubuntu/sd_pbl2/IoT/certificates/a504e91ba6-certificate.pem.crt")

client.connect()
#print("Client Connected")

def publish(topic, msg):
    client.publish(topic, str(msg), 0)

def subscribe(topic, qos, callback):
    client.subscribe(topic, qos, callback)

def __historico__(client, userdata ,mensage ):
    slug = mensage.topic.split("/")[0]
#    print(f"editando historico {slug} :", mensage.payload.decode("utf-8"))
    coisa = Coisa.objects.get(slug=slug)
    hist = Historico.objects.filter(coisa=coisa)
    msg = json.loads(mensage.payload.decode("utf-8").replace("ld",""))
    today = date.today()
    d1 = today.strftime("%d/%m/%Y")
    hist = hist.filter(date=d1)
    if(len(hist)>0):
        hist = hist[0]
        hist.tempo_ligado+=msg["tempo"]
    else:
        hist = Historico(date = d1, tempo_ligado=msg["tempo"],coisa=coisa)
#    print(hist.tempo_ligado)
    hist.save()
#    print(f'o historico do dia {hist.date} foi somado em {msg["tempo"]}s ficando com um total de: {hist.tempo_ligado}s')
    
def __iniciar__(client, userdata ,mensage ):
    slug = mensage.topic.split("/")[0]
    coisa = Coisa.objects.get(slug=slug)
    msg = {"novo_estado": 1 if (coisa.estado_lampada) else 0}
    publish(f'{slug}/OnOff',msg)
    temporizadores = Temporizadores.objects.filter(coisa=coisa)
    for t in temporizadores:
        msg = { "tempo":t.horario,
                "estado": 1 if(t.estado) else 0,
                "posição":t.pos,
                "is_add": 1,
                "should_be_trigger": 1 }
        publish(f'{slug}/temporizador',msg)
#    print(f"A coisa {slug} foi iniciada, sendo enviado ultimo estado da lampada e os temporizadores")

coisas={}

def __get_timer__(client, userdata ,mensage ):
    slug = mensage.topic.split("/")[0]
    msg = json.loads(mensage.payload.decode("utf-8"))
    msg["timer_on"] = msg["timer_on"]==1
    try:
        coisas[slug]["timer"]=msg["timer"] if msg["timer_on"] else "00:00:00"
        coisas[slug]["estado_timer"]=msg["timer_on"]
    except:
#        print("entrou me except")
        coisas[slug] = {"estado_lampada":0,
                        "timer":msg["timer"] if msg["timer_on"] else "00:00:00",
                        "estado_timer": msg["timer_on"]}
        publish(f'{coisa.slug}/get_tempo',"")
#    print( f'O valor do timer na placa é {coisas[slug]["timer"]} e ele esta ',"ligado" if (coisas[slug]["estado_timer"]) else "desligado" )

def __estado__(client, userdata ,mensage ):
    slug = mensage.topic.split("/")[0]
    coisa = Coisa.objects.get(slug=slug)
    msg = msg = json.loads(mensage.payload)
    try:
        coisas[slug]["estado_lampada"] = (msg["Estado"]==1)
        coisa.estado_lampada = (msg["Estado"]==1)
    except:
#        print("entrou me except")
        coisas[slug] = {"estado_lampada":msg["Estado"]==1,
                        "timer":None,
                        "estado_timer":False}
        coisa.estado_lampada = msg["Estado"]==1
    coisa.save()
#    print(f" o estado de {slug} foi alterado para ","ligado" if (coisa.estado_lampada) else "desligado")


def confirma_coisa(slug):
    try:
        coisas[slug]["estado_lampada"] =None
    except:
      adiciona_coisa(slug)
      coisas[slug]["estado_lampada"] =None
    publish(f'{coisa.slug}/get_tempo',"")
    for a in range(7000000):
        try:
            if(coisas[slug]["estado_lampada"] !=None or  coisas[slug]["timer"] !=None or coisas[slug]["estado_timer"] !=None):
#                print("returning true")
                return True
        except:
            pass
#    print("returning false")
    return False

def adiciona_coisa(slug):
    subscribe(f'{coisa.slug}/Estado',0, __estado__)
    subscribe(f'{coisa.slug}/Iniciar',0, __iniciar__)
    subscribe(f'{coisa.slug}/get_timer',0, __get_timer__)
    subscribe(f'{coisa.slug}/Alterar_Historico',0,__historico__)
    coisas[coisa.slug] = {"estado_lampada":None,
                        "timer":None,
                        "estado_timer":None}

#Inicia as coisas que estao salvas na db
for coisa in  Coisa.objects.all():
    subscribe(f'{coisa.slug}/Estado',0, __estado__)
    subscribe(f'{coisa.slug}/Iniciar',0, __iniciar__)
    subscribe(f'{coisa.slug}/get_timer',0, __get_timer__)
    subscribe(f'{coisa.slug}/Alterar_Historico',0,__historico__)
    coisas[coisa.slug] = {"estado_lampada":None,
                        "timer":None,
                        "estado_timer":None}
    #publish(f'{coisa.slug}/get_tempo',"{}")
