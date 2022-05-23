#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
#include <ESPAsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <HX711.h>

HX711 scale;

const char* ssid = "NeoNIC_WiFi";
const char* password = "THENEOSTORM69";

AsyncWebServer server(80);
String RIP = "192.168.43.125";
String RP = "5000";

float units;
float res = 0;

void setup() {
  Serial.begin(9600);

  scale.begin(0, 4);

  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
  }
  Serial.print("Set and done! IP: ");
  Serial.println(WiFi.localIP());
  
  delay(1000);
  scale.tare();
  Serial.println("checkpoint 0");
  scale.set_scale(-1.6);
  Serial.println("checkpoint 1");
  server.on("/", HTTP_GET, [](AsyncWebServerRequest* request){
    request->send(200, "text/plain", "Weigher online!");
  });

  Serial.println("checkpoint 2");

  server.on("/recv", HTTP_GET, [](AsyncWebServerRequest* request){
    Serial.println("I've got request signal!");
    request->send(200, "text/plain", String(res));
  });

  Serial.println("checkpoint 3");
  server.begin();
  Serial.println("Weigher online!");
}

void loop() {
  for (int i = 0; i < 10; i++) {
    units = + scale.get_units(), 10;
  }
  res = units * 0.0035274;
  delay(100);
}
