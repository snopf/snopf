// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#ifndef __change_secret_h__
#define __change_secret_h__

#include <avr/eeprom.h>
#include <stdint.h>

// Definitions of the device's secret

// Length of the secret in bytes (16 bytes == 128 Bit)
#define SECRET_LENGTH 16

// Current secret for password generation stored in EEPPROM
extern uint8_t ee_secret[SECRET_LENGTH] EEMEM;

// Placeholder for a temporary secret in case of secret change
extern uint8_t ee_tmp_secret[SECRET_LENGTH] EEMEM;

// Clears the eeprom space for the secret
void secret_clear(void);

// Clears the eeprom space for the temporary secret
void secret_clear_tmp(void);

#endif
