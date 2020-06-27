// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#ifndef __sha256_h__
#define __sha256_h__

#include <stdint.h>

/*
 * SHA256 implementation for a single chunk, consisting of the 128 bit secret
 * on the devices EEPROM and the 128 bit message
 */

// Calculate SHA256 for the secret+message and store the result in hash
void sha256(uint32_t hash[8],
            const uint32_t secret[8],
            const uint32_t message[4],
            uint32_t sha256_w[64]);

#endif
