import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
import time as t
import json

myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient("MyClient")

myAWSIoTMQTTClient.configureEndpoint("at9zi9dd4t3sg-ats.iot.us-east-1.amazonaws.com", 8883)
myAWSIoTMQTTClient.configureCredentials("L:\Programming-related\\nodeMCUcertificates\\AmazonRootCA1.pem", 
                                "L:\Programming-related\\nodeMCUcertificates\\6e0a74dd84-private.pem.key",
                                "L:\Programming-related\\nodeMCUcertificates\\6e0a74dd84-certificate.pem.crt")

myAWSIoTMQTTClient.connect()
print("Client Connected")

def publish(topic, msg):
    myAWSIoTMQTTClient.publish(topic, str(msg), 0)

def subscribe(topic, qos, callback):
    myAWSIoTMQTTClient.subscribe(topic, qos, callback)