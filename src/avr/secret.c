// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#include "secret.h"

// Definition of the current secret
uint8_t ee_secret[SECRET_LENGTH] EEMEM = {
    0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37,
    0x38, 0x39, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35
};

// Placeholder for the temporarily new secret in case of secret change
uint8_t ee_tmp_secret[SECRET_LENGTH] EEMEM = {
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
};

// Clear the given eeprom secret array
static void _clear_secret(uint8_t *arr)
{
    for (uint8_t i = 0; i < SECRET_LENGTH; i++) {
        eeprom_update_byte(&arr[i], 0);
    }   
}

void secret_clear_tmp(void)
{
    _clear_secret(ee_tmp_secret);
}

void secret_clear(void)
{
    _clear_secret(ee_secret);
}
