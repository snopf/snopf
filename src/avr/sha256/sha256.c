// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

// SHA256 implementation for concatenated secret of a fixed length of 128 bit
// and a message of a fixed length of 128 bit

#ifdef TEST_NO_MCU
#define PROGMEM
#else
#include <avr/pgmspace.h>
#include <avr/eeprom.h>
#endif

#include "sha256.h"
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

// Initial hash values
static const PROGMEM uint32_t h0[8] = {0x6a09e667, 0xbb67ae85, 0x3c6ef372,
                                       0xa54ff53a, 0x510e527f, 0x9b05688c,
                                       0x1f83d9ab, 0x5be0cd19};

// Initial round constants
static const PROGMEM uint32_t k[64] = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1,
    0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
    0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
    0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
    0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
    0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2};

// Initialize message schedule array as global variable to make sure
// we have allocated the memory
static uint32_t w[64];

// Working variables a, b, c, d, e, f, g, h
static uint32_t h[8];

static uint32_t s0, s1, temp1, temp2, maj, ch;

void sha256_calculate_hash(uint8_t hash[32], const uint8_t secret[16],
                           const uint8_t message[16])
{
    // The original message of 256 bits has to be extended by
    // a single one bit
    // K zero bits with K := 512 - 64 - 1 - 256
    // 64 bits representing the big endian integer 256
    // We then have to copy this message to the first 16 words of the
    // message schedule array w

    // First part is the secret to be read from EEPROM on the MCU
    for (uint8_t i = 0, j = 0; i < 4; i++, j += 4) {
#ifdef TEST_NO_MCU
        w[i] = (((uint32_t)secret[j]) << 24) | (((uint32_t)secret[j + 1]) << 16)
               | (((uint16_t)secret[j + 2]) << 8) | (secret[j + 3]);
#else
        w[i] = ((uint32_t)eeprom_read_byte(&secret[j])) << 24;
        w[i] |= ((uint32_t)eeprom_read_byte(&secret[j + 1])) << 16;
        w[i] |= ((uint16_t)eeprom_read_byte(&secret[j + 2])) << 8;
        w[i] |= eeprom_read_byte(&secret[j + 3]);
#endif
    }

    // Second part is the concatenated message
    for (uint8_t i = 4, j = 0; i < 8; i++, j += 4) {
        w[i] = (((uint32_t)message[j]) << 24)
               | (((uint32_t)message[j + 1]) << 16)
               | (((uint16_t)message[j + 2]) << 8) | (message[j + 3]);
    }

    // Add the single one bit in big endian convention
    w[8] = ((uint32_t)1) << 31;
    
    // Add the K zero bits
    memset(&w[9], 0, 15-9);
    
    // Original message length as 64 bit big endian integer
    w[15] = ((uint16_t)1) << 8;

    // Extend the first 16 words into the remaining 48 words
    for (uint8_t i = 16; i < 64; i++) {
        s0 = SIG0(w[i - 15]);
        s1 = SIG1(w[i - 2]);
        w[i] = w[i - 16] + s0 + w[i - 7] + s1;
    }

    // Initialize working variables
    for (uint8_t i = 0; i < 8; i++) {
#ifdef TEST_NO_MCU
        h[i] = h0[i];
#else
        h[i] = pgm_read_dword(&h0[i]);
#endif
    }

    // Compression function main loop
    for (uint8_t i = 0; i < 64; i++) {
        s1 = EP1(h[4]);
        ch = CH(h[4], h[5], h[6]);
#ifdef TEST_NO_MCU
        temp1 = h[7] + s1 + ch + w[i] + k[i];
#else
        temp1 = h[7] + s1 + ch + w[i] + pgm_read_dword(&k[i]);
#endif
        
        s0 = EP0(h[0]);
        maj = MAJ(h[0], h[1], h[2]);
        temp2 = s0 + maj;

        // 0 1 2 3 4 5 6 7
        // a b c d e f g h
        for (uint8_t i = 7; i > 0; i--) {
            h[i] = h[i - 1];
        }
        h[4] += temp1;
        h[0] = temp1 + temp2;
    }
    
    // As a security measure we clear the w[] array asap to avoid having
    // the secret in RAM longer than necessary
    memset(w, 0, 64);

    // Add compressed chunk to hash value
    for (uint8_t i = 0; i < 8; i++) {
#ifdef TEST_NO_MCU
        h[i] += h0[i];
#else
        h[i] += pgm_read_dword(&h0[i]);
#endif
    }

    // Shift hash to little endian and store it in the char array
    for (uint8_t i = 0; i < 4; i++) {
        for (uint8_t k = 0, j = 0; k < 8; k++, j += 4) {
#ifdef TEST_NO_MCU
            hash[i + j] = (h[k] >> (24 - i * 8));
#else
            hash[i + j] = (h[k] >> (24 - i * 8));
#endif
        }
    }
}
