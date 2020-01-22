// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#ifndef __sha256_h__
#define __sha256_h__

#include <stdint.h>

/*
 * SHA256 implementation for a single chunk, consisting of the 128 bit secret
 * on the devices EEPROM and the 128 bit message
 */

// Calculate SHA256 for the secret+message and store the result in hash[]
void sha256_calculate_hash(uint8_t hash[32], const uint8_t secret[16],
                           const uint8_t message[16]);

#endif
