/*Developed by M V Subrahmanyam - https://www.linkedin.com/in/veera-subrahmanyam-mediboina-b63997145/
Project: AWS | NodeMCU ESP32 Tutorials
Electronics Innovation - www.electronicsinnovation.com

GitHub - https://github.com/VeeruSubbuAmi
YouTube - http://bit.ly/Electronics_Innovation

Upload date: 07 October 2019

AWS Iot Core

This example needs https://github.com/esp8266/arduino-esp8266fs-plugin

It connects to AWS IoT server then:
- publishes "hello world" to the topic "outTopic" every two seconds
- subscribes to the topic "inTopic", printing out any messages
*/



#include "FS.h"
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <NTPClient.h>
#include <WiFiUdp.h>

// Update these with values suitable for your network.

//begin connecting to the wifi

const char* ssid = "ssid";
const   char* password = "password";

WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org");

const char* AWS_endpoint = "at9zi9dd4t3sg-ats.iot.us-east-1.amazonaws.com"; //MQTT broker ip

//en connecting to the wifi

//begin callback(receiving messages)

void callback(char* topic, byte* payload, unsigned int length) {
  if(strcmp(topic, "inTopic") == 0){
    //digitalWrite(2, HIGH);
    //delay(1500);
    Serial.print("Message arrived [");
    Serial.print(topic);
    Serial.print("] ");
    for (int i = 0; i < length; i++) {
      Serial.print((char)payload[i]);
    }
    Serial.println();
  }
  else if(strcmp(topic, "Light/onoff") == 0){
    //Serial.print("Message arrived [");
    //Serial.print(topic);
    //Serial.print("] ");
    //for (int i = 0; i < length; i++) {
      //Serial.print((char)payload[i]);
    //}
    //Serial.println();
    
    String r_payload = "";
    for (int i=0;i<length;i++) {
      r_payload += (char)payload[i];
    }
    //add
    for (int i = 0; i < length; i++) {
      Serial.print(r_payload[i]);
    }
    Serial.println();
    //add
    if(r_payload == "on"){
      digitalWrite(2, LOW);
      Serial.print("Hi");
    }
    else if(r_payload == "off"){
      digitalWrite(2, HIGH);
      Serial.print("Hi");
    }
  }
}

//end callback

//begin publishing variables

WiFiClientSecure espClient;
PubSubClient client(AWS_endpoint, 8883, callback, espClient); //set MQTT port number to 8883 as per //standard
long lastMsg = 0;
char msg[50];
int value = 0;
//end publishing variables


//begin setup wifi

void setup_wifi() {

  delay(10);
  // We start by connecting to a WiFi network
  espClient.setBufferSizes(512, 512);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  timeClient.begin();
  while (!timeClient.update()) {
    timeClient.forceUpdate();
  }

  espClient.setX509Time(timeClient.getEpochTime());

}

//end setup wifi


//begin reconnect to try and connect with MQTT

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("ESPthing")) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      client.publish("outTopic", "hello world");
      // ... and resubscribe
      client.subscribe("inTopic");
      client.subscribe("Light/#");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");

      char buf[256];
      espClient.getLastSSLError(buf, 256);
      Serial.print("WiFiClientSecure SSL error: ");
      Serial.println(buf);

      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

//end reconnect

//begin setup

void setup() {

  Serial.begin(115200);
  Serial.setDebugOutput(true);
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);
  setup_wifi();
  delay(1000);
  if (!SPIFFS.begin()) {
    Serial.println("Failed to mount file system");
    return;
  }

  Serial.print("Heap: "); Serial.println(ESP.getFreeHeap());

  // Load certificate file
  File cert = SPIFFS.open("/cert.der", "r"); //replace cert.crt eith your uploaded file name
  if (!cert) {
    Serial.println("Failed to open cert file");
  }
  else
    Serial.println("Success to open cert file");

  delay(1000);

  if (espClient.loadCertificate(cert))
    Serial.println("cert loaded");
  else
    Serial.println("cert not loaded");

  // Load private key file
  File private_key = SPIFFS.open("/private.der", "r"); //replace private eith your uploaded file name
  if (!private_key) {
    Serial.println("Failed to open private cert file");
  }
  else
    Serial.println("Success to open private cert file");

  delay(1000);

  if (espClient.loadPrivateKey(private_key))
    Serial.println("private key loaded");
  else
    Serial.println("private key not loaded");

  // Load CA file
  File ca = SPIFFS.open("/ca.der", "r"); //replace ca eith your uploaded file name
  if (!ca) {
    Serial.println("Failed to open ca ");
  }
  else
    Serial.println("Success to open ca");

  delay(1000);

  if (espClient.loadCACert(ca))
    Serial.println("ca loaded");
  else
    Serial.println("ca failed");

  Serial.print("Heap: "); Serial.println(ESP.getFreeHeap());
}

//end setup

//begin loop where the messge qeues are handled

void loop() {

  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  long now = millis();
  if (now - lastMsg > 2000) {
    lastMsg = now;
    ++value;
    snprintf (msg, 75, "{\"message\": \"hello world #%ld\"}", value);
    Serial.print("Publish message: ");
    Serial.println(msg);
    client.publish("outTopic", msg);
    Serial.print("Heap: "); Serial.println(ESP.getFreeHeap()); //Low heap can cause problems
  }
  //digitalWrite(2, HIGH); // turn the LED on (HIGH is the voltage level)
  //delay(1500); // wait for a second
  //digitalWrite(2, LOW); // turn the LED off by making the voltage LOW
  //delay(1500); // wait for a second
}

//end loop
