#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
#include <ESPAsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <Servo.h>

Servo servo;

const char* ssid = "NeoNIC_WiFi";
const char* password = "THENEOSTORM69";

AsyncWebServer server(80);
String RIP = "192.168.43.125";
String RP = "5000";

bool rotate = false;
int angle = 0;
int interval = 0;

void setup() {
  Serial.begin(9600);

  servo.attach(2);
  servo.write(0);

  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
  }
  Serial.print("Set and done! IP: ");
  Serial.println(WiFi.localIP());

  server.on("/", HTTP_GET, [](AsyncWebServerRequest* request){
    request->send(200, "text/plain", "Dispenser online!");
  });

  server.on(
    "/dispense", 
    HTTP_POST, 
    [](AsyncWebServerRequest* request){
      Serial.println("I've got dispense signal!");  
    }, 
    NULL,
    [](AsyncWebServerRequest* request, uint8_t* data, size_t len, size_t index, size_t total) {
      DynamicJsonDocument bodyJSON(1024);
      deserializeJson(bodyJSON, data, len);
      angle = bodyJSON["angle"];
      interval = bodyJSON["interval"];
      
      Serial.print("Angle: ");
      Serial.print(angle);
      Serial.print(", delay: ");
      Serial.println(interval);

      rotate = true;
      request->send(200, "text/plain", "OK");
    });

  server.begin();
  Serial.println("Dispenser online!");
}

void loop() {
  if (rotate) {
    for (int i = 0; i <= angle; i += 1) {
      servo.write(i);
      delay(interval);
    }
    for (int i = angle; i > 0; i -= 1) {
      servo.write(i);
      delay(interval);
    }
    rotate = false;
  }
  delay(100);
}
