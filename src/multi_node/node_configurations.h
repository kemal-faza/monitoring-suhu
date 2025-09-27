// === KONFIGURASI MULTIPLE NODES ===
// File ini berisi konfigurasi untuk beberapa node ESP32
// Copy bagian yang sesuai ke file esp32_node.cpp

// ================================
// NODE 001 - AREA KIRI BAWAH
// ================================
/*
const char* NODE_ID = "node_001";
const float POS_X = 25.0;
const float POS_Y = 25.0;
#define DHT_PIN 4
#define LED_MQTT_PIN 12
*/

// ================================  
// NODE 002 - AREA KANAN BAWAH
// ================================
/*
const char* NODE_ID = "node_002";
const float POS_X = 75.0;
const float POS_Y = 25.0;
#define DHT_PIN 4
#define LED_MQTT_PIN 12
*/

// ================================
// NODE 003 - AREA TENGAH ATAS  
// ================================
/*
const char* NODE_ID = "node_003";
const float POS_X = 50.0;
const float POS_Y = 75.0;
#define DHT_PIN 4
#define LED_MQTT_PIN 12
*/

// ================================
// NODE 004 - AREA KIRI ATAS
// ================================
/*
const char* NODE_ID = "node_004";
const float POS_X = 15.0;
const float POS_Y = 85.0;
#define DHT_PIN 4
#define LED_MQTT_PIN 12
*/

// ================================
// NODE 005 - AREA KANAN ATAS
// ================================
/*
const char* NODE_ID = "node_005";
const float POS_X = 85.0;
const float POS_Y = 85.0;
#define DHT_PIN 4
#define LED_MQTT_PIN 12
*/

// === KONFIGURASI TIMING PER NODE ===
// Variasikan interval untuk menghindari collision MQTT

// Node 001: MQTT_INTERVAL = 5000ms
// Node 002: MQTT_INTERVAL = 5500ms  
// Node 003: MQTT_INTERVAL = 6000ms
// Node 004: MQTT_INTERVAL = 6500ms
// Node 005: MQTT_INTERVAL = 7000ms

// === ALTERNATIVE PIN CONFIGURATIONS ===
// Jika menggunakan pin yang berbeda per node

// Node 001: DHT_PIN = 4,  LED_MQTT_PIN = 12
// Node 002: DHT_PIN = 5,  LED_MQTT_PIN = 13  
// Node 003: DHT_PIN = 18, LED_MQTT_PIN = 19
// Node 004: DHT_PIN = 21, LED_MQTT_PIN = 22
// Node 005: DHT_PIN = 25, LED_MQTT_PIN = 26

// === KOORDINAT FIELD REFERENCE ===
// Field Size: 100m x 100m
// Origin (0,0) = Bottom Left Corner
// Max (100,100) = Top Right Corner
//
//  (0,100) +----------+ (100,100)
//          |          |
//          |   FIELD  |  
//          |          |
//    (0,0) +----------+ (100,0)
//
// Contoh Layout 5 Node:
//
//  NODE_004      NODE_005
//  (15,85)       (85,85)
//      •           •
//
//        NODE_003
//        (50,75)  
//          •
//
//  NODE_001      NODE_002  
//  (25,25)       (75,25)
//      •           •