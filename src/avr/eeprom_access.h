// Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#ifndef __eeprom_access_h__
#define __eeprom_access_h__

#include <stdint.h>
#include <string.h>

#ifdef TEST_NO_MCU
    #define EEMEM
    #define eeprom_read_block(dst, src, count) (memcpy(dst, src, count))
    #define eeprom_update_block(src, dst, count) (memcpy(dst, src, count))
    #define eeprom_read_byte(x) *(x)
    #define eeprom_read_dword(x) *(x)
#else
    #include <avr/eeprom.h>
#endif

struct EEPROM_LAYOUT {
    uint8_t dummy;
    uint8_t secret[32];
    uint32_t sha256_k[64];
    uint32_t sha256_h0[8];
    uint8_t kb_delay;
    uint8_t keycodes[64][2];
} __attribute__((packed));

extern EEMEM struct EEPROM_LAYOUT eeprom_layout;

// Write new data to eeprom we got from the USB host to the
// unprotected eeprom space
// Return 1 if all data successfully written, else 0
int8_t ee_access_write_unprotected(uint16_t addr, uint8_t* data, uint8_t len);

// Write new data to eeprom we got from the USB host to the
// protected eeprom space (Secret + SHA256 constants)
// Return 1 if all data successfully written, else 0
int8_t ee_access_write_protected(uint16_t addr, uint8_t* data, uint8_t len);

// Get keyboard modifier for given key index
// Returns 0 if we try to access space outside the unprotected scope
int8_t ee_access_get_key_modifier(uint8_t index, uint8_t* modifier);

// Get keyboard keycode for given key index
// Returns 0 if we try to access space outside the unprotected scope
int8_t ee_access_get_key_code(uint8_t index, uint8_t* keycode);

// Read the keyboard delay value to the buffer
int8_t ee_access_read_kb_delay(uint8_t* buffer);

// Get keyboard modifiers + keycodes for given key index
// Returns 0 if we try to access space outside the unprotected scope
int8_t ee_access_read_keycodes(uint8_t buffer[86], uint8_t _begin, uint8_t _num);

#endif  //__eeprom_access_h__
