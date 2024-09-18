// -- CONFIGURACIONES Y LIBRERIAS -- //
// Importa las librerias WiFi
#include <WiFi.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>

// importa la Librerias DHT
#include <DHT.h>    
#include <DHT_U.h>

// Configuración de la red Wi-Fi
const char* ssid = "OPPO Reno7";
const char* password = "ingesitos#1";

// Configuración del broker MQTT
const char* mqttServer = "192.168.117.58"; //Nuestra IP del PC es la que ponemos aqui
const int mqttPort = 1883;

//  - Configuracion DHT11 - //
int SENSOR = 23;     // pin DATA de DHT11 a pin 22
// Variables de sensado
float t;
float h;
DHT dht(SENSOR, DHT11);   // creacion del objeto, cambiar segundo parametro

// Configuracion Motores
// Motores A
int IN1 = 14;      
int IN2 = 12;      
int ENA = 13;      
// Motores B
int IN4 = 4;      
int IN3 = 2;      
int ENB = 15;      

// Configuracion Servo
Servo myServo;


// ==================================================================== //

// -- Instancias de cliente Wi-Fi y MQTT -- //
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

// -- Función de callback para mensajes MQTT. Recibimos Datos -- //
void callback(char* topic, byte* payload, unsigned int length) {
    Serial.print("Mensaje recibido en el tópico: ");
    Serial.println(topic);

    // Cambiar a vool
    String message;
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    Serial.print("Mensaje: ");
    Serial.println(message);

    // - Control del Motor A basado en el mensaje - //
    if (message == "MAon") {
      // Habilita motor A (giro en un sentido)
      digitalWrite(ENA, HIGH);  
      digitalWrite(IN1, LOW); 
      digitalWrite(IN2, HIGH);  
      mqttClient.publish("ESP/MotorA", "Encendido");
    } else if (message == "MAoff") {
        digitalWrite(ENA, LOW); 
        mqttClient.publish("ESP/MotorA", "Apagado");
    }

    // - Control del Motor B basado en el mensaje - //
    if (message == "MBon") {
       // Habilita motor B (giro en un sentido)
      digitalWrite(ENB, HIGH);  
      digitalWrite(IN3, LOW);
      digitalWrite(IN4, HIGH);  
      mqttClient.publish("ESP/MotorB", "Encendido");
    } else if (message == "MBoff") {
        digitalWrite(ENB, LOW); 
        mqttClient.publish("ESP/MotorB", "Apagado");
    }

    // - Control del Servo Motor basado en el mensaje - //
    int angle = message.toInt();  // Convierte el mensaje a un número entero
    if (angle >= 0 && angle <= 180) {
       myServo.write(angle);
    } else {
       Serial.println("Valor no válido para el servo");
    }
}

// Funcion de Conectar al broker MQTT
void reconnect() {
    while (!mqttClient.connected()) {
        Serial.print("Intentando conectar al broker MQTT...");
        if (mqttClient.connect("ESP32Client")) {
            Serial.println("Conectado");
            // Control Motores
            mqttClient.subscribe("ESP/MotorA");
            mqttClient.subscribe("ESP/MotorB");
            mqttClient.subscribe("ESP/Servo");
        } else {
            Serial.print("Fallido, rc=");
            Serial.print(mqttClient.state());
            Serial.println(" Intentando de nuevo en 5 segundos");
            delay(5000);
        }
    }
}

// ==================================================================== //

void setup() {
    // Inicializar el puerto serie
    Serial.begin(115200);
    
    // inicializacion de sensor DHT11
    dht.begin();   

    // Inicilizacion servomotor
    myServo.attach(22);

    // -  Inicializacion de Motor A - //
    pinMode(IN1, OUTPUT); 
    pinMode(IN2, OUTPUT);  
    pinMode(ENA, OUTPUT);   

    // - Inicializacion de Motor B - //
    pinMode(IN4, OUTPUT); 
    pinMode(IN3, OUTPUT);  
    pinMode(ENB, OUTPUT);

    // Conectar a la red Wi-Fi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("Conectado a Wi-Fi...");

    // Configurar el servidor MQTT
    mqttClient.setServer(mqttServer, mqttPort);
    mqttClient.setCallback(callback);
}

void loop() {
    t = dht.readTemperature();  // obtencion de valor de temperatura
    h = dht.readHumidity();   // obtencion de valor de humedad

    // -- ENVIO TEMPÉRATURAS -- //
    String temp = String(t);
    mqttClient.publish("ESP/Temperatura", temp.c_str());    
    Serial.print("Temperatura: ");  
    Serial.print(t);

    String hum = String(h);
    mqttClient.publish("ESP/Humedad", hum.c_str());
    Serial.print(" Humedad: ");
    Serial.println(h);
    delay(2000);
  
    if (!mqttClient.connected()) {
        reconnect();
    }
    mqttClient.loop();
}