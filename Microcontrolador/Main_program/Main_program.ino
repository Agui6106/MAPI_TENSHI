// -- CONFIGURACIONES Y LIBRERIAS -- //
// Importa las librerias WiFi
#include <WiFi.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>

// importa la Librerias DHT
#include <DHT.h>    
#include <DHT_U.h>

// Importa la libreria para el giroscopio
#include <Wire.h>

// Importa la libreria para el GPS
#include <TinyGPS++.h>

// Configuración de la red Wi-Fi
const char* ssid = "OPPO Reno7";
const char* password = "ingesitos#1";

// Configuración del broker MQTT
const char* mqttServer = "192.168.252.58"; //Nuestra IP del PC es la que ponemos aqui
const int mqttPort = 1883;

//  - Configuracion DHT11 - //
int SENSOR = 23;     // pin DATA de DHT11 a pin 23
// Variables de sensado
float t;
float h;
DHT dht(SENSOR, DHT11);   // creacion del objeto, cambiar segundo parametro

// Configuracion Motores
// Motores A
#define IN1 14      
#define IN2 12      
int ENA = 13;      
// Motores B
#define IN4 4      
#define IN3 2      
int ENB = 15; 
#define FREQ 5000
#define PWM_CHANNEL 0 
#define RESOLUTION 8
int duty_cycle = 200; //seria el 100 porciento, registro de 8 bits

// Configuracion Servo
Servo myServo;

// Configuración Sensor Ultrasónico
#define trigPin 18     // Pin de Trigger
#define echoPin 19    // Pin de Echo
long duration;
float distance;

// Configuración Sensor Ultrasónico 2
#define trigPin2 26   // Pin de Trigger
#define echoPin2 27   // Pin de Echo
long duration2; 
float distance2;

// Coniguración Sensor Infrarrojo 1
int infrarrojo1 = 5;  // Pin de Sensor Infrarrojo 1

// Configuración Sensor Infrarrojo 2
int infrarrojo2 = 25;  // Pin de Sensor Infrarrojo 2

// Configuración Giroscopio
// pin 22 SCL / pin 21 SDA
//Direccion I2C de la IMU
#define MPU 0x68
 
//conversion de unidades 
#define A_R 16384.0 // 32768/2
#define G_R 131.0 // 32768/250
 
//Conversion de radianes a grados 180/PI
#define RAD_A_DEG = 57.295779
 
//MPU-6050 da los valores en enteros de 16 bits
//Valores RAW
int16_t AcX, AcY, AcZ, GyX, GyY, GyZ;
 
//Angulos
float Acc[2];
float Gy[3];
float Angle[3];

String valores;

long tiempo_prev;
float dt;

// Configuración del GPS
TinyGPSPlus gps;

#define RXD2 16  // Cambia al pin que usas para RX del ESP32
#define TXD2 17  // Cambia al pin que usas para TX del ESP32

double LATITUDE , LONGITUDE;
String latitude="", longitude="";
double SPEED;
String speed="";
String MSG;

// ==================================================================== //

// -- Instancias de cliente Wi-Fi y MQTT -- //
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

// -- Función de callback para mensajes MQTT. Recibimos Datos -- //
void callback(char* topic, byte* payload, unsigned int length) {      //Datos que mandamos desde la app
    //Serial.print("Mensaje recibido en el tópico: ");
    //Serial.println(topic);

    // Cambiar a vool
    String message;
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    //Serial.print("Mensaje: ");
    //Serial.println(message);

    // - Control del Motor A basado en el mensaje - //
    if (message == "Up") {
      // Habilita motor A (giro hacia adelante)
      digitalWrite(ENA, HIGH);  
      digitalWrite(IN1, LOW); 
      digitalWrite(IN2, HIGH);
      // Habilita motor B (giro hacia adelante)
      digitalWrite(ENB, HIGH); 
      digitalWrite(IN3, LOW);
      digitalWrite(IN4, HIGH);
    } else if (message == "Down") {
      // Habilita motor A (giro hacia atras)
      digitalWrite(ENA, HIGH);  
      digitalWrite(IN1, HIGH); 
      digitalWrite(IN2, LOW);
      // Habilita motor B (giro hacia atras)
      digitalWrite(ENB, HIGH); 
      digitalWrite(IN3, HIGH);
      digitalWrite(IN4, LOW);
    } else if (message == "Left"){
      // Habilita motor A (giro hacia atras)
      digitalWrite(ENA, HIGH);  
      digitalWrite(IN1, HIGH); 
      digitalWrite(IN2, LOW);
      // Habilita motor B (giro hacia adelante)
      digitalWrite(ENB, HIGH); 
      digitalWrite(IN3, LOW);
      digitalWrite(IN4, HIGH);
    } else if (message == "Right"){
      // Habilita motor A (giro hacia adelante)
      digitalWrite(ENA, HIGH);  
      digitalWrite(IN1, HIGH); 
      digitalWrite(IN2, LOW);
      // Habilita motor B (giro hacia atras)
      digitalWrite(ENB, HIGH); 
      digitalWrite(IN3, HIGH);
      digitalWrite(IN4, LOW);
    } else{
      // Apagar ambos motores
      digitalWrite(ENA, LOW);
      digitalWrite(ENB, LOW);
    }

    // - Control del Servo Motor basado en el mensaje - //
    int angle = 0;
    myServo.write(180);
    if (message == "D_LFT") {
      myServo.write(angle - 10);
      mqttClient.publish("ESP/Response", "Servo -10°");
      
      } else if (message == "D_RGT"){
        myServo.write(angle + 10);
        mqttClient.publish("ESP/Response", "Servo +10°");

      }

    /*
    float angle = message.toFloat();  // Convierte el mensaje a un número entero
    if (angle >= 0 && angle <= 180) {
       myServo.write(angle);
    } else {
       Serial.println("Valor no válido para el servo");
    }
    */

}

// Funcion de Conectar al broker MQTT
void reconnect() {
    while (!mqttClient.connected()) {
        //Serial.print("Intentando conectar al broker MQTT...");
        if (mqttClient.connect("ESP32Client")) {
            Serial.println("Conectado");
            // Control Motores
            //mqttClient.subscribe("ESP/MotorX");
            //mqttClient.subscribe("ESP/MotorY");
            mqttClient.subscribe("ESP/Servo");
        } else {
            //Serial.print("Fallido, rc=");
            //Serial.print(mqttClient.state());
            //Serial.println(" Intentando de nuevo en 5 segundos");
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
    myServo.attach(33);

    // -  Inicializacion de Motor A - //
    pinMode(IN1, OUTPUT); 
    pinMode(IN2, OUTPUT);  
    // pinMode(ENA, OUTPUT);   

    // - Inicializacion de Motor B - //
    pinMode(IN4, OUTPUT); 
    pinMode(IN3, OUTPUT);  
    // pinMode(ENB, OUTPUT);

    //ledcSetup(PWM_CHANNEL, FREQ, RESOLUTION);
    ledcAttach(IN1, FREQ, RESOLUTION);
    digitalWrite(IN2, LOW);

    ledcAttach(IN3, FREQ, RESOLUTION);
    digitalWrite(IN4, LOW);

    // - Inicializacion de Sensor Ultrasónico - //
    pinMode(trigPin, OUTPUT);
    pinMode(echoPin, INPUT);
    digitalWrite(trigPin, LOW);//Inicializamos el pin con 0

    // - Inicializacion de Sensor Ultrasónico 2 - //
    pinMode(trigPin2, OUTPUT);
    pinMode(echoPin2, INPUT);

    // - Inicializacion de Sensor Infrarrojo 1 - //
    pinMode(infrarrojo1, INPUT);

    // - Inicializacion de Sensor Infrarrojo 2 - //
    pinMode(infrarrojo2, INPUT);

    // - Inicializacion de Giroscopio - //
    Wire.begin();
    Wire.beginTransmission(MPU);
    Wire.write(0x6B);  // PWR_MGMT_1 registro
    Wire.write(0);     // despierta el modulo
    Wire.endTransmission(true);

    // - Inicializacion de GPS - //
    Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);  // Configuramos Serial con los pines RX y TX);

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

void loop() { // Datos que recibimos del ESP32
    if (!mqttClient.connected()) {
        reconnect();
    }
    mqttClient.loop();
    
    // -- LECTURA DE SENSORES -- //
    t = dht.readTemperature();  // Temperatura
    h = dht.readHumidity();     // Humedad

    // -- SENSOR ULTRASONICO -- //
    // Sensor 1
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);          //Enviamos un pulso de 10us
    digitalWrite(trigPin, LOW);
  
    duration = pulseIn(echoPin, HIGH); //obtenemos el ancho del pulso
    distance = duration/59;             //escalamos el tiempo a una distancia en cm

    // Sensor 2 
    digitalWrite(trigPin2, HIGH);
    delayMicroseconds(10);          //Enviamos un pulso de 10us
    digitalWrite(trigPin2, LOW);
  
    duration2 = pulseIn(echoPin2, HIGH); //obtenemos el ancho del pulso
    distance2 = duration2/59;             //escalamos el tiempo a una distancia en cm
    delay(200);

    // -- SENSOR INFRARROJOS -- //
    int valueInf1 = 0;
     valueInf1 = digitalRead(infrarrojo1);
    int valueInf2 = 0;
     valueInf2 = digitalRead(infrarrojo2);

    String state1 = "";
    String state2 = "";

    // Procesamiento de las lecturas de infrarrojo para detectar obstáculos
    // Sensor 1
    if (valueInf1 == LOW) {
        //mqttClient.publish("ESP/Infra-1", "collision");
        state1 = "collision";
        //Serial.println("Peligro de colisión inminente. Sending to Broker...");
    } else if (valueInf1 == HIGH){
      //mqttClient.publish("ESP/Infra-1", "clear");
      state1 = "clear";
    }

    // Sensor 2
    if (valueInf2 == LOW) {
        //mqttClient.publish("ESP/Infra-1", "collision");
        state2 = "collision";
        //Serial.println("Peligro de colisión inminente. Sending to Broker...");
    } else if (valueInf2 == HIGH){
      //mqttClient.publish("ESP/Infra-1", "clear");
      state2 = "clear";
    }

  // -- LECTURA DE GIROSCOPIO -- //
    //Leer los valores del Acelerometro de la IMU
   Wire.beginTransmission(MPU);
   Wire.write(0x3B); //Pedir el registro 0x3B - corresponde al AcX
   Wire.endTransmission(false);
   Wire.requestFrom(MPU,6,true);   //A partir del 0x3B, se piden 6 registros
   AcX=Wire.read()<<8|Wire.read(); //Cada valor ocupa 2 registros
   AcY=Wire.read()<<8|Wire.read();
   AcZ=Wire.read()<<8|Wire.read();
 
   //A partir de los valores del acelerometro, se calculan los angulos Y, X
   //respectivamente, con la formula de la tangente.
   Acc[1] = atan(-1*(AcX/A_R)/sqrt(pow((AcY/A_R),2) + pow((AcZ/A_R),2)))*RAD_TO_DEG;
   Acc[0] = atan((AcY/A_R)/sqrt(pow((AcX/A_R),2) + pow((AcZ/A_R),2)))*RAD_TO_DEG;
 
   //Leer los valores del Giroscopio
   Wire.beginTransmission(MPU);
   Wire.write(0x43);
   Wire.endTransmission(false);
   Wire.requestFrom(MPU,6,true);   //A partir del 0x43, se piden 6 registros
   GyX=Wire.read()<<8|Wire.read(); //Cada valor ocupa 2 registros
   GyY=Wire.read()<<8|Wire.read();
   GyZ=Wire.read()<<8|Wire.read();
 
   //Calculo del angulo del Giroscopio
   Gy[0] = GyX/G_R;
   Gy[1] = GyY/G_R;
   Gy[2] = GyZ/G_R;

   dt = (millis() - tiempo_prev) / 1000.0;
   tiempo_prev = millis();
 
   //Aplicar el Filtro Complementario
   Angle[0] = 0.98 *(Angle[0]+Gy[0]*dt) + 0.02*Acc[0];
   Angle[1] = 0.98 *(Angle[1]+Gy[1]*dt) + 0.02*Acc[1];

   //Integración respecto del tiempo paras calcular el YAW
   Angle[2] = Angle[2]+Gy[2]*dt;

   // -- LECTURA DE GPS -- //
   while (Serial2.available() > 0)  {
     gps.encode(Serial2.read());
   }

    if (millis() > 5000 && gps.charsProcessed() < 10)
      {
        //Serial.println(F("No GPS detected: check wiring."));
        while(true);
      }  
      

    if (gps.location.isValid())
        {
          LATITUDE = gps.location.lat(), 6 ;
          latitude = String(LATITUDE,6);
          
          LONGITUDE = gps.location.lng(), 6 ;
          longitude = String(LONGITUDE,6);
          SPEED = gps.speed.kmph();
          speed = String(SPEED,3);

          MSG="";
          MSG = MSG + "https://www.google.com/maps/search/?api=1&query=";
          MSG = MSG + latitude;
          MSG = MSG + ",";
          MSG = MSG + longitude;
          MSG = MSG + "\n";
          
          //Serial.println(MSG);
        }

    else
    {
      //Serial.println("INVALID");
    }
    
    // delay(2000);

    
    // -- ENVIO DE DATOS -- //
    String mensaje = String(t) + "°C," + 
                     String(h) + " %," +
                     String(distance) + " cm," + 
                     String(distance2) + " cm," + 
                     state1 + "," +
                     state2 + "," +
                     String(Angle[0]) + "°," +
                     String(Angle[1]) + "°," +
                     String(Angle[2]) + "°," +
                     latitude + "," + 
                     longitude + "\n";


    mqttClient.publish("ESP/Sensors", mensaje.c_str());    
    Serial.print(mensaje);
    /*
    Serial.println("Temperatura: " + String(t));
    Serial.println("Humedad: " + String(h));
    Serial.println("Distancia 1: " + String(distance));
    Serial.println("Distancia 2: " + String(distance2));
    Serial.println("Col State 1: " + String(state1));
    Serial.println("Col State 2: "  + String(state2));
    Serial.println("Angulo X: " + String(Angle[0]));
    Serial.println("Angulo Y: " + String(Angle[1]));
    Serial.println("Angulo Z: " + String(Angle[2]));
    Serial.println("Latitud: " + String(latitude));
    Serial.println("Longitud: " + String(longitude));
    */

    delay(500);

/*
    // Motores 
    duty_cycle =   + 10;
    Serial.println(duty_cycle);
    if(duty_cycle > 255)
    {
      duty_cycle = 0;
    }
    
    ledcWrite(PWM_CHANNEL, duty_cycle);

        // -- ENVIO DISTANCIA SENSOR ULTRASONICO 2 -- //
    String dist2 = String(distance2);
    mqttClient.publish("ESP/Ultra-Distancas2", dist2.c_str());
    Serial.print("Distancia2: ");
    Serial.println(distance2);
    delay(200);
 
    // -- ENVIO ESTADO SENSOR INFRARROJO 2 -- //
    


    // -- ENVIO ESTADO SENSOR INFRARROJO 2 -- //
    String infra2 = String(digitalRead(infrarrojo2));
    mqttClient.publish("ESP/Infra-2", infr2.c_str());
    int valueInf2 = 0;
    value = digitalRead(infrarrojo2);  //lectura digital de pin

    if (value == HIGH) {
            Serial.println("Detectando obstaculo");
        }

    delay(2000);
  */
    
}
