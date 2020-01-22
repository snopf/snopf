// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#ifdef TEST_NO_MCU
#define PROGMEM
#include <assert.h>
#else
#include <avr/pgmspace.h>
#endif

#include "z85.h"

//  Maps base 256 to base 85
static const char z85_map[85 + 1] PROGMEM = {
    "0123456789"
    "abcdefghij"
    "klmnopqrst"
    "uvwxyzABCD"
    "EFGHIJKLMN"
    "OPQRSTUVWX"
    "YZ.-:+=^!/"
    "*?&<>()[]{"
    "}@%$#"};

static const uint32_t z85_divisor[5] PROGMEM = {
    52200625, 614125, 7225, 85, 1
    // 85*85*85*85, 85*85*85, 85*85, 85, 1
    // Using 85*85*85*85 directly does not work as GCC interprets this
    // as a int8_t multiplication
};

void z85_encode_chunk(char z85_encoded[5], const uint8_t sha256_hash[4])
{
    static uint32_t value;
    static uint32_t divisor;

    value = 0;
    for (uint8_t i = 0; i < 4; i++) {
        value = value * 256 + sha256_hash[i];
    }

    for (uint8_t i = 0; i < 5; i++) {
#ifdef TEST_NO_MCU
        divisor = z85_divisor[i];
        z85_encoded[i] = z85_map[value / divisor % 85];
#else
        divisor = pgm_read_dword(&z85_divisor[i]);
        z85_encoded[i] =
            pgm_read_byte(&(z85_map[(uint8_t)(value / divisor % 85)]));
#endif
    }
}
