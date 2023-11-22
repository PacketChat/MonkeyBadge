#define MICROPY_HW_BOARD_NAME "MonkeyBadge"
#define MICROPY_HW_MCU_NAME "ESP32 WROOM 32E"
// Disabling bluetooth will free approximately 200k of flash
#define MICROPY_PY_BLUETOOTH (0)
#define MICROPY_BLUETOOTH_NIMBLE (0)
#define MICROPY_HW_ENABLE_MDNS_QUERIES (0)
#define MICROPY_HW_ENABLE_MDNS_RESPONDER (0)
