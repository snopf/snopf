// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

// SHA256 implementation for concatenated secret of a fixed length of 128 bit
// and a message of a fixed length of 128 bit
// This implementation discards the Big-Endianess of the input/output data

#include "sha256.h"

#include "../eeprom_access.h"
#include <string.h>

// Macros taken from Brad Conte's crypto-algorithms SHA256 implementation
// brad@bradconte.com
// https://github.com/B-Con/crypto-algorithms/blob/master/sha256.c
#define ROTLEFT(a, b) (((a) << (b)) | ((a) >> (32 - (b))))
#define ROTRIGHT(a, b) (((a) >> (b)) | ((a) << (32 - (b))))

#define CH(x, y, z) (((x) & (y)) ^ (~(x) & (z)))
#define MAJ(x, y, z) (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))
#define EP0(x) (ROTRIGHT(x, 2) ^ ROTRIGHT(x, 13) ^ ROTRIGHT(x, 22))
#define EP1(x) (ROTRIGHT(x, 6) ^ ROTRIGHT(x, 11) ^ ROTRIGHT(x, 25))
#define SIG0(x) (ROTRIGHT(x, 7) ^ ROTRIGHT(x, 18) ^ ((x) >> 3))
#define SIG1(x) (ROTRIGHT(x, 17) ^ ROTRIGHT(x, 19) ^ ((x) >> 10))

void sha256(uint32_t hash[8],
            const uint32_t secret[8],
            const uint32_t message[4],
            uint32_t sha256_w[64])
{
    
    static uint32_t s0, s1, temp1, temp2, maj, ch;

    // First part is the secret to be read from EEPROM on the MCU
    eeprom_read_block(sha256_w, secret, 32);

    // Second part is the message
    memcpy(sha256_w + 8, message, 16);
    
    // Add the single one bit in big endian convention
    sha256_w[12] = ((uint32_t)1) << 31;
    
    // Add the K zero bits
    memset(sha256_w + 13, 0, 4);
    
    // Original message length (384) as 64 bit big endian integer
    sha256_w[14] = 0;
    sha256_w[15] = 0x180;
    
    // Extend the first 16 words into the remaining 48 words
    for (uint8_t i = 16; i < 64; i++) {
        s0 = SIG0(sha256_w[i - 15]);
        s1 = SIG1(sha256_w[i - 2]);
        sha256_w[i] = sha256_w[i - 16] + s0 + sha256_w[i - 7] + s1;
    }

    // Initialize working variables
    eeprom_read_block(hash, eeprom_layout.sha256_h0, 32);

    // Compression function main loop
    for (uint8_t i = 0; i < 64; i++) {
        s1 = EP1(hash[4]);
        ch = CH(hash[4], hash[5], hash[6]);
        temp1 = hash[7] + s1 + ch + sha256_w[i] + eeprom_read_dword(
            eeprom_layout.sha256_k +i);
        s0 = EP0(hash[0]);
        maj = MAJ(hash[0], hash[1], hash[2]);
        temp2 = s0 + maj;

        for (uint8_t i = 7; i > 0; i--) {
            hash[i] = hash[i - 1];
        }
        hash[4] += temp1;
        hash[0] = temp1 + temp2;
    }
    
    // Add compressed chunk to hash value
    for (uint8_t i = 0; i < 8; i++) {
        hash[i] += eeprom_read_dword(eeprom_layout.sha256_h0 + i);
    }
}
