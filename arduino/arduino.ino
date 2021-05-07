#include "FS.h"
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>

struct temporizador {
  String tempo;
  bool estado;
  bool is_on = false;
  bool will_be_trigger;
};
/*
  SETUP PLACA
*/

//setando as informaçoes da rede
const char* id_rede = "FIBRA-1032";
const char* senha_rede = "0Z38019489";

WiFiUDP udp;
NTPClient tempo_obj(udp, "b.ntp.br", -3 * 3600, 60000);
//endpoint AWS
const char* AWS_endpoint = "a1hhzdnhqam0eu-ats.iot.us-east-1.amazonaws.com";
//setando a função que vai ser chamada quando uma mensagem chegar
void callback(char* topic, byte* payload, unsigned int length);

WiFiClientSecure espClient;
PubSubClient MQTT(AWS_endpoint, 8883, callback, espClient);

/*
  SETUP VARIAVEIS GLOBAIS
*/

// Variaveis pra o codigo
String timer = "00:00:00";
bool timer_on = false;

int estado_lampada=1;
unsigned long ligado_at;

const int DEFOUT_JSON_BIT_SIZE = 256;

const int len_temporizadores = 10;
temporizador temporizadores[len_temporizadores];

//Nome dispostivo
const String nome_dispositivo = "Lampada1";

/*
  FUNÇOES
*/

/*
  Esta função altera o estado da lampada
  @param novo_estado é uma bool que sera o novo estado da lampada, true para ligado e false para desligado
    para o caso de ligado o estado é alterado estado da variavel que  guarda o valor do estado da lampada, guarda o tempo no qual a lampada foi ligada e liga a lampada ( envia HIGH pro pino 2 )
    para o caso de desligadao ele calcula o tempo que a lampada fico ligado e manda um publish no topico Soma_historico_Wh com o valor em milisegundos que a lampada fico on no codigo "tempo", muda a variavel de estado da lampada, zera a variavel que guarda o instante q a lampada estava on e apaga a lampada ( envia LOW no pino 2 )
*/
void mudar_estado_lampada( int novo_estado ) {
  Serial.print("entrando na função de muda estado mudando para: ");
  if (novo_estado == 1 && estado_lampada == 0) {
    Serial.println("Ligando");
    digitalWrite(LED_BUILTIN, LOW); // Manda LOW aqui pq a logica do led é invertida
    ligado_at = tempo_obj.getEpochTime();
    estado_lampada = novo_estado;
  } else if (novo_estado == 0 && estado_lampada == 1) {
    Serial.println("Apagando");
    digitalWrite(LED_BUILTIN, HIGH); // manda HIGH aqui pq a logica do led é invertida
    unsigned long now = tempo_obj.getEpochTime();
    ligado_at = now - ligado_at;
    char msg[75];
    snprintf (msg, 75, "{\"tempo\": %uld}", ligado_at);
    MQTT.publish("Lampada1/Alterar_Historico", msg);
    Serial.print("historico alterado: ");
    Serial.println(msg);
    ligado_at = 0;
    estado_lampada = novo_estado;
  } else {
    Serial.print ("nenhuma ação foi tomada variaveis de estatus-> estado atual: ");
    Serial.print (estado_lampada);
    Serial.print (" estado novo: ");
    Serial.println (novo_estado);
  }
}
/*
  Esta função publica o estado da lampada como inteiro, 0 pra falso ( apagada ) e nao 0 pra true ( acessa ), no codigo "Estado"
*/
void publish_lampada() {
  Serial.println( "enviando estado da lampada" );
  char msg[60];
  snprintf (msg, 60, "{\"Estado\": %d}", estado_lampada);
  MQTT.publish("Lampada1/Estado", msg);
}

/*
  Esta função seta o valor do timer, e seta a flag que indica se o timer esta ligado ou desligado
  @param tempo, tipo String, sendo o horario que que o evento sera trigado, ex: caso timer seja de 30 min e o horario atual 15:32:23 o valor de tempo dever ser 16:02:23
  @param is_ligado bool indicando se o timer deve ser ligado ou desligado
*/
void set_timer(String tempo, bool is_ligado) {
  Serial.print("Criando timer para inverter o estado da lampada em (s):");
  Serial.println(tempo);
  timer_on = is_ligado == 1 ? true : false;
  timer = tempo;
}

/*
  Esta função publica o timer no broker MQTT
*/
void get_timer() {
  Serial.print("Publicando timer");
  char msg[160];
  char buff[30];
  for(int a =0; a<timer.length();a++){
    buff[a]=timer[a];
    }
  buff[timer.length()] = 0;
  if(timer_on){
    snprintf (msg, 160, "{\"timer\": \"%s\", \"timer_on\":1}", buff);
  }else{
    snprintf (msg, 160, "{\"timer\": \"%s\", \"timer_on\":0}", buff);
    }
  Serial.println(msg);
  MQTT.publish("Lampada1/get_timer", msg);
}

/*
  Esta função atualiza os dados de um determinado temporizador do vetor.
  @param tempom tipo String, sendo o horario que o temporizador deve ser acionado, ex: 19:34:59
  @param estado um bool indicando se a lampada vai acender ou apagar
  @param pos int que indica a posição do temporizador no vetor de temporizadores
  @param is_add bool dizendo se o temporizador foi adicionado (true) ou removido (false)
  @param should_be_trigger bool indicando se o temporizador deve ser trigado ainda nesse ciclo de 24h de funcionamento da placa
*/
void set_temporizador(String tempo, bool estado, int pos, bool is_add, bool should_be_trigger) {
  temporizadores[pos].tempo = tempo;
  temporizadores[pos].estado = estado;
  temporizadores[pos].is_on = is_add == 1 ? true : false;
  temporizadores[pos].will_be_trigger = should_be_trigger;
}

/*
  Função que recebe a mensagem do MQTT e chama os devidos procedimentos para serem executados
  @param topic é um vetor de char que contem o titulo do topico a qual a mensagme pertence e sera usadao para chamar o procedimento que lidara com essa mensagem
  @param payload é um vetor de bytes e consiste no binario contendo a mensagem enviada
  @param length é um unsigned int que tem o tamanho do payload
*/
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.println("] ");
  DynamicJsonDocument doc(DEFOUT_JSON_BIT_SIZE);
  deserializeJson(doc, payload);
  serializeJson(doc, Serial);
  Serial.println();
  if ( strcmp(topic,"Lampada1/OnOff") == 0 ) {
    mudar_estado_lampada(doc["novo_estado"]);
  } else if ( strcmp(topic, "Lampada1/get_tempo") == 0 ) {
    publish_lampada();
    get_timer();  
  } else if ( strcmp(topic, "Lampada1/set_timer") == 0 ) {
    set_timer(doc["set_timer"], doc["is_ligado"]);
  } else if ( strcmp(topic, "Lampada1/temporizador") == 0 ) {
    set_temporizador(doc["tempo"], doc["estado"], doc["posição"], doc["is_add"], doc["should_be_trigger"]);
  };
  topic = "";
}
/**
* Este procedimento é responsavel por realizar a conecção com o wifi
**/
void conectar_wifi() {
  // We start by connecting to a WiFi network
  espClient.setBufferSizes(512, 512);
  Serial.println();
  Serial.print("Tentando conectar com: ");
  Serial.println(id_rede);

  WiFi.begin(id_rede, senha_rede);

  while (WiFi.status() != WL_CONNECTED) {
    delay(200);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi conectado");
  tempo_obj.begin();
  while (!tempo_obj.update()) {
    tempo_obj.forceUpdate();
  }
  espClient.setX509Time(tempo_obj.getEpochTime());

}
/**
*função para Conectar com o MQTT
**/
void conectar_mqtt() {
  while (!MQTT.connected()) {
    Serial.print("Tentando conectar com o MQTT: ");
    // parque que faz o request pra conectar
    if (MQTT.connect("ESPthing")) {
      Serial.println("Conectado");
      //se inscrevendo nos topicos que serao constantemente ouvidos pela placa
      MQTT.subscribe("Lampada1/OnOff");
      MQTT.subscribe("Lampada1/get_tempo");
      MQTT.subscribe("Lampada1/set_timer");
      MQTT.subscribe("Lampada1/temporizador");
    } else {
      Serial.print("Nao conectado, rc=");
      Serial.print(MQTT.state());
      Serial.println(" Nova tentativa em 1 segundo");
      delay(1000);
    }
  }
}
/**
* Função padrao do arduino, é executada 1 vez quando o despositivo entra em execução
**/
void setup() {
  Serial.begin(9600); // inicia "console"
  Serial.setDebugOutput(true);
  // Pino do led como saida.
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(0, INPUT_PULLUP);
  //tenta conectar com wifi
  conectar_wifi();
  delay(1000);
  if (!SPIFFS.begin()) {
    Serial.println("Falha na inicialização");
    return;
  }
  for ( int a = 0; a < len_temporizadores; a++ )
    temporizadores[a].is_on = false;

  // Carregando certificados do AWS
  File cert = SPIFFS.open("/crt.der", "r");
  cert ? Serial.println("Certificado aberto com sucesso") : Serial.println("Falha ao abrir o certificado");
  espClient.loadCertificate(cert) ? Serial.println("Certificado caregado") : Serial.println("Falha ao caregar o certificado");

  File private_key = SPIFFS.open("/private.der", "r");
  private_key ? Serial.println("Chave privada aberta com sucesso") : Serial.println("Falha em abrir a chave privada");
  espClient.loadPrivateKey(private_key) ? Serial.println("Chave privada carregada com sucesso") : Serial.println("Chave privada não carregada");

  File ca = SPIFFS.open("/ca.der", "r");
  ca ? Serial.println("AWS CA aberto com sucesso") : Serial.println("AWS CA não foi abertoaberto");
  espClient.loadCACert(ca) ? Serial.println("AWS CA caregado") : Serial.println("AWS CA não carregado");

  conectar_mqtt();
//  Serial.println(tempo_obj.getFormattedTime());
  mudar_estado_lampada(1);
  ligado_at = tempo_obj.getEpochTime();
  MQTT.publish("Lampada1/Iniciar","{}");
}

bool was_button_pushed = false, was_already_sent = false;

/**
* É uma função padrao do arduino e sera executada infinitamente apos o setup até o despositivo ser desligado
**/
void loop() {
  // se nao estiver conectado a amazon conecte
  if (!MQTT.connected()) {
    conectar_mqtt();
  }
  MQTT.loop();
  //coletamos qual o millis de agora
  String now = tempo_obj.getFormattedTime();
  if (timer_on != false && now >= timer) { // se passamos do horario do timer  e ele nao foi ativado ainda ativamos ele
    Serial.println("timer trigado"); 
    mudar_estado_lampada( (estado_lampada == 0) ? 1 : 0 );
   timer_on = false;
  }
  if (now == "00:00:00" ) { // a cada 24h re-armamos os temporizadores
    for ( int a = 0; a < len_temporizadores; a++ )
      temporizadores[a].will_be_trigger = true;
    // Como deve ter o historico diario a cada final de dia se a lampada estiver acessa enviamos o tempo que ela ficou acessa e zeramos a variavel que guarda esse tempo na memoria
    if(estado_lampada==1){
      char msg[75];
      snprintf (msg, 75, "{\"tempo\": %ld}", tempo_obj.getEpochTime() - ligado_at );
      ligado_at = tempo_obj.getEpochTime();
      MQTT.publish("Lampada1/Alterar_Historico", msg);
    }
    Serial.println( "Houve virada de dia" );
  }// para cada temporizador o tempo de agora for maior que o de acionalo E não tivermos acionado ainda E ele deve ser usado o trigamos
  for (int a = 0; a < len_temporizadores; a++) {
    if ( temporizadores[a].will_be_trigger && now >= temporizadores[a].tempo && temporizadores[a].is_on) {
      mudar_estado_lampada( temporizadores[a].estado );
      temporizadores[a].will_be_trigger = false;
    }
  }// pin 0 é o botao
  if ( was_button_pushed && !was_already_sent) {
    if(WiFi.status() == WL_CONNECTED){
      char msg[75];
      snprintf (msg, 75, "{\"novo_estado\": %i}", estado_lampada == 1 ? 0 : 1);
      MQTT.publish("Lampada1/OnOff" , msg);
      }else{
        mudar_estado_lampada(estado_lampada == 1 ? 0 : 1);
        }
    was_already_sent = true;
  }
  was_already_sent = was_button_pushed;
  was_button_pushed = digitalRead(0) == 0 ? true : false;
}
