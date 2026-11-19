/**
 * ============================================================================
 * Verona Project - LoRa Wireless Communication
 * ============================================================================
 * 
 * Supports:
 *  - SX1276 / SX1278 (e.g., Ai-Thinker Ra-02) LoRa Transceivers
 *  - ESP32 / Arduino Nano / Uno microcontrollers
 *  - Bi-directional communication (Transceiver), Beacon (TX), or Listener (RX)
 *  - Real-time Serial console input to send manual LoRa messages
 *  - Signal quality metrics (RSSI and SNR reporting)
 * ============================================================================
 */

#include <Arduino.h>
#include <SPI.h>
#include <LoRa.h>
#include "config.h"

// --- Global State Variables ---
static uint32_t packetCounter = 0;
static uint32_t lastTxTime = 0;
static String serialInputBuffer = "";

// --- Function Declarations ---
void initLoRa();
void sendLoRaPacket(const String &payload);
void checkIncomingPackets();
void handleSerialCommands();

void setup() {
    Serial.begin(MONITOR_BAUD);
    while (!Serial && millis() < 3000); // Wait for Serial Monitor on USB CDC boards

    Serial.println();
    Serial.println(F("=================================================="));
    Serial.println(F("           VERONA PROJECT: LORA SYSTEM            "));
    Serial.println(F("=================================================="));
    Serial.print(F("Operating Mode: "));
#if (NODE_MODE == MODE_TRANSCEIVER)
    Serial.println(F("TRANSCEIVER (Two-Way Communication)"));
#elif (NODE_MODE == MODE_TRANSMITTER)
    Serial.println(F("TRANSMITTER (Telemetry Beacon)"));
#elif (NODE_MODE == MODE_RECEIVER)
    Serial.println(F("RECEIVER (Continuous Listening)"));
#endif

    initLoRa();

    Serial.println(F("[READY] System initialized."));
    Serial.println(F("[TIP] Type any message in the Serial Monitor to transmit."));
    Serial.println(F("--------------------------------------------------"));
}

void loop() {
    uint32_t currentMillis = millis();

    // 1. Process serial input from user to send custom messages
    handleSerialCommands();

    // 2. Check for incoming LoRa packets (in Transceiver and Receiver modes)
#if (NODE_MODE == MODE_TRANSCEIVER || NODE_MODE == MODE_RECEIVER)
    checkIncomingPackets();
#endif

    // 3. Periodic automatic transmission (in Transceiver and Transmitter modes)
#if (NODE_MODE == MODE_TRANSCEIVER || NODE_MODE == MODE_TRANSMITTER)
    if (currentMillis - lastTxTime >= TX_INTERVAL_MS) {
        lastTxTime = currentMillis;

        packetCounter++;
        String message = "VERONA_BEACON#" + String(packetCounter) + 
                         "|Uptime:" + String(currentMillis / 1000) + "s";
        sendLoRaPacket(message);
    }
#endif
}

/**
 * Initializes SPI and the LoRa transceiver module.
 */
void initLoRa() {
    Serial.print(F("[INFO] Initializing SPI bus... "));
#if defined(ESP32)
    SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
#else
    SPI.begin();
#endif
    Serial.println(F("OK"));

    Serial.print(F("[INFO] Configuring LoRa pins (SS="));
    Serial.print(LORA_SS);
    Serial.print(F(", RST="));
    Serial.print(LORA_RST);
    Serial.print(F(", DIO0="));
    Serial.print(LORA_DIO0);
    Serial.println(F(")..."));
    LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);

    Serial.print(F("[INFO] Starting LoRa at "));
    Serial.print(LORA_BAND / 1E6, 1);
    Serial.print(F(" MHz... "));

    if (!LoRa.begin(LORA_BAND)) {
        Serial.println(F("FAILED!"));
        Serial.println(F("[ERROR] LoRa transceiver not detected."));
        Serial.println(F("[CHECK] 1. Verify wiring between MCU and LoRa module."));
        Serial.println(F("[CHECK] 2. Ensure adequate 3.3V power supply (LoRa requires up to 120mA peak)."));
        Serial.println(F("[CHECK] 3. Check pin definitions in 'include/config.h'."));
        while (1) {
            delay(1000);
        }
    }
    Serial.println(F("SUCCESS"));

    // Apply advanced radio configuration
    LoRa.setSyncWord(LORA_SYNC_WORD);
    LoRa.setSpreadingFactor(LORA_SPREADING_FAC);
    LoRa.setSignalBandwidth(LORA_SIGNAL_BW);
    LoRa.setCodingRate4(LORA_CODING_RATE);
    LoRa.setTxPower(LORA_TX_POWER);

    Serial.println(F("[INFO] LoRa radio parameters set:"));
    Serial.print(F("       - Sync Word: 0x"));
    Serial.println(LORA_SYNC_WORD, HEX);
    Serial.print(F("       - Spreading Factor: SF"));
    Serial.println(LORA_SPREADING_FAC);
    Serial.print(F("       - Bandwidth: "));
    Serial.print(LORA_SIGNAL_BW / 1E3, 0);
    Serial.println(F(" kHz"));
    Serial.print(F("       - Tx Power: "));
    Serial.print(LORA_TX_POWER);
    Serial.println(F(" dBm"));
}

/**
 * Transmits a payload over LoRa.
 */
void sendLoRaPacket(const String &payload) {
    Serial.print(F("[TX] Transmitting: \""));
    Serial.print(payload);
    Serial.print(F("\" ... "));

    LoRa.beginPacket();
    LoRa.print(payload);
    LoRa.endPacket();

    Serial.println(F("Done."));
}

/**
 * Checks for received packets and prints signal metrics.
 */
void checkIncomingPackets() {
    int packetSize = LoRa.parsePacket();
    if (packetSize == 0) {
        return; // No packet received
    }

    String incomingData = "";
    while (LoRa.available()) {
        incomingData += (char)LoRa.read();
    }

    int rssi = LoRa.packetRssi();
    float snr = LoRa.packetSnr();

    Serial.println();
    Serial.println(F("--------------------------------------------------"));
    Serial.print(F("[RX] Incoming Packet (Length: "));
    Serial.print(packetSize);
    Serial.println(F(" bytes)"));
    Serial.print(F("     Payload: \""));
    Serial.print(incomingData);
    Serial.println(F("\""));
    Serial.print(F("     Signal:  RSSI = "));
    Serial.print(rssi);
    Serial.print(F(" dBm | SNR = "));
    Serial.print(snr, 2);
    Serial.println(F(" dB"));
    Serial.println(F("--------------------------------------------------"));

#if (NODE_MODE == MODE_TRANSCEIVER)
    // If we receive a beacon or ping, respond with an acknowledgment
    if (incomingData.startsWith("VERONA_BEACON") || incomingData.startsWith("PING")) {
        delay(200); // Brief turn-around delay
        String ackPayload = "VERONA_ACK|RSSI:" + String(rssi);
        sendLoRaPacket(ackPayload);
    }
#endif
}

/**
 * Reads user input from the Serial Monitor and transmits it as a custom packet.
 */
void handleSerialCommands() {
    while (Serial.available()) {
        char c = (char)Serial.read();
        if (c == '\r') {
            continue; // Ignore carriage return
        }
        if (c == '\n') {
            serialInputBuffer.trim();
            if (serialInputBuffer.length() > 0) {
                Serial.print(F("[CONSOLE] User command: \""));
                Serial.print(serialInputBuffer);
                Serial.println(F("\""));
                sendLoRaPacket("VERONA_MSG:" + serialInputBuffer);
                serialInputBuffer = "";
            }
        } else {
            serialInputBuffer += c;
        }
    }
}