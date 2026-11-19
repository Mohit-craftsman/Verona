#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

// ============================================================================
// VERONA PROJECT - CONFIGURATION SETTINGS
// ============================================================================

// --- Operational Mode ---
// Choose one of the following modes:
// 1 = TRANSCEIVER (Bi-directional communication / Ping-Pong)
// 2 = TRANSMITTER (Periodic telemetry beacon)
// 3 = RECEIVER (Continuous listening mode)
#define NODE_MODE 1

#define MODE_TRANSCEIVER 1
#define MODE_TRANSMITTER 2
#define MODE_RECEIVER    3

// --- LoRa Radio Frequency ---
// 433E6 : Asia, Europe (433 MHz) - Standard Ra-02 modules
// 868E6 : Europe (868 MHz)
// 915E6 : North America (915 MHz)
#define LORA_BAND 433E6

// --- Radio Parameters ---
#define LORA_SYNC_WORD      0xF3       // Unique sync word to isolate network
#define LORA_SPREADING_FAC  7          // Spreading Factor (6 to 12)
#define LORA_SIGNAL_BW      125E3      // Bandwidth (125 kHz)
#define LORA_CODING_RATE    5          // Coding Rate 4/5 (5 to 8)
#define LORA_TX_POWER       17         // Transmission power in dBm (2 to 20)

// --- Transmission Timing ---
#define TX_INTERVAL_MS      5000       // Interval between automatic transmissions (ms)

// ============================================================================
// HARDWARE PIN DEFINITIONS
// ============================================================================

#if defined(BOARD_TTGO_LORA32)
    // LilyGO TTGO LoRa32 v1.0 Pinout
    #define LORA_SCK    5
    #define LORA_MISO   19
    #define LORA_MOSI   27
    #define LORA_SS     18
    #define LORA_RST    14
    #define LORA_DIO0   26

#elif defined(BOARD_ARDUINO_NANO)
    // Arduino Uno / Nano Pinout
    #define LORA_SCK    13
    #define LORA_MISO   12
    #define LORA_MOSI   11
    #define LORA_SS     10
    #define LORA_RST    9
    #define LORA_DIO0   2

#else
    // Generic ESP32 + SX1278 (e.g. Ra-02) Pinout
    #define LORA_SCK    18
    #define LORA_MISO   19
    #define LORA_MOSI   23
    #define LORA_SS     5
    #define LORA_RST    14
    #define LORA_DIO0   26
#endif

#ifndef MONITOR_BAUD
    #define MONITOR_BAUD 115200
#endif

#endif // CONFIG_H