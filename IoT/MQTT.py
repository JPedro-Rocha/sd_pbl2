import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
from .models import *
import json
from datetime import date
from time import sleep


client = AWSIoTPyMQTT.AWSIoTMQTTClient("meu_client")

client.configureEndpoint("at9zi9dd4t3sg-ats.iot.us-east-1.amazonaws.com", 8883)
client.configureCredentials("C:\\Users\\dfc15\\Downloads\\AmazonRootCA1.pem", 
                                "C:\\Users\\dfc15\\Downloads\\a504e91ba6-private.pem.key",
                                "C:\\Users\\dfc15\\Downloads\\a504e91ba6-certificate.pem.crt")

client.connect()
print("Client Connected")

def publish(topic, msg):
    client.publish(topic, str(msg), 0)

def subscribe(topic, qos, callback):
    client.subscribe(topic, qos, callback)

def __historico__(client, userdata ,mensage ):
    slug = mensage.topic.split("/")[0]
    coisa = Coisa.objects.get(slug=slug)
    hist = Historico.objects.filter(coisa=coisa)
    msg = json.loads(mensage.payload)
    today = date.today()
    d1 = today.strftime("%d/%m/%Y")
    if( len(hist) > 1 ):
        hist = hist.filter(date=d1)
    if(len(hist)>0):
        hist = hist[0]
        hist.tempo_ligado+=msg["tempo"]

    else:
        hist = Historico(date = d1, tempo_ligado=msg["tempo"],preço=00.00,coisa=coisa)
    
    hist.save()

    print(f'o historico do dia {hist.date} foi somado em {msg["tempo"]}ms ficando com um total de: {hist.tempo_ligado}ms')

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
    print("A coisa {slug} foi iniciada, sendo enviado ultimo estado da lampada e os temporizadores")
coisas={}

def __get_timer__(client, userdata ,mensage ):
    slug = mensage.topic.split("/")[0]
    msg = msg = json.loads(mensage.payload)
    timer=msg["timer"]
    estado_timer=msg["timer_on"]
    print( f"O valor do timer na placa é {timer} e ele esta ","ligado" if (estado_timer) else "desligado" )

def __estado__(client, userdata ,mensage ):
    slug = mensage.topic.split("/")[0]
    coisa = Coisa.objects.get(slug=slug)
    msg = msg = json.loads(mensage.payload)
    try:
        coisas[slug]["estado_lampada"] = coisa.estado_lampada = msg["Estado"]==1
    except:
        cisas[slug] = {"estado_lampada":msg["Estado"]==1,
                        "timer":None,
                        "estado_timer":False}
        coisa.estado_lampada = msg["Estado"]==1
    coisa.save()
    print(f" o estado de {slug} foi alterado para ","ligado" if (estado_lampada) else "desligado")

for coisa in  Coisa.objects.all():
    subscribe(f'{coisa.slug}/Estado',0, __estado__)
    subscribe(f'{coisa.slug}/Iniciar',0, __iniciar__)
    subscribe(f'{coisa.slug}/get_timer',0, __get_timer__)
    subscribe(f'{coisa.slug}/Alterar_Historico',0,__historico__)
    publish(f'{coisa.slug}/get_tempo',"")
