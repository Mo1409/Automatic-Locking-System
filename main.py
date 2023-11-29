import network
import machine
import time
import dht
import ujson
from umqtt.simple import MQTTClient
from machine import Pin,PWM
import utime
from time import sleep 
from f import Servo

tranca = "oi"
Motion_Detected = False  #Global variable to hold the state of motion sensor

def handle_interrupt(Pin):           #defining interrupt handling function
 global Motion_Detected
 Motion_Detected = True

#servo = Pin(5,Pin.OUT)
sensor = Pin(26,Pin.IN)

sensor.irq(trigger=Pin.IRQ_RISING, handler=handle_interrupt)
pwm = PWM(Pin(15), freq=50, duty=0)

Servo(pwm, 180)

# MQTT Server Parameters
MQTT_CLIENT_ID = "conect demo"
MQTT_BROKER    = "broker.mqttdashboard.com"
MQTT_TOPIC_SEND = "exp.criativas/enviar"
MQTT_TOPIC_RECEIVE = "exp.criativas/receber" 
MQTT_USER      = "123456"
MQTT_PASSWORD  = "123456"

#função com a resposta do topico selecionado
def callback(topic, msg):
    global tranca
    print("Mensagem recebida: ", msg.decode())
    tranca = msg.decode()
    #client.publish(MQTT_TOPIC_RECEIVE, "Funcionou!!!!!")

#Parte da comunicação do driver virtual do
print("Connecting to WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '')
while not sta_if.isconnected():
  print(".", end="")
  time.sleep(0.1)
print(" Connected!")

print("Connecting to MQTT server... ", end="")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)


#####Criando retorno de informação
client.set_callback(callback)

####Conectando no cliente
client.connect()
print("Connected!")
#Fazendo inscrição no tópico "mensagens" para receber mensagens
client.subscribe(MQTT_TOPIC_RECEIVE)


while True:
    client.check_msg();
    if Motion_Detected:
        # Publicação da mensagem que será enviada
        client.publish(MQTT_TOPIC_SEND, "MOVIMENTO DETECTADO")
        while (tranca == "oi"):
            client.check_msg();
        print(tranca)
        if tranca == "S":
            for i in range (180, 85, -5):
                Servo(pwm, i)
                utime.sleep(0.1)
            sleep(20)
            print("Porta Trancada!")
            Servo(pwm, 180)
            Motion_Detected = False
        else:
            Motion_Detected = False
            print("Porta Trancada. Timeout de 15 minutos." )
            sleep(900)
            print("Timeout acabou!")



