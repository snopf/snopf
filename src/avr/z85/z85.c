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

void z85_encode_chunk(char z85_encoded[5], const uint8_t* chunk)
{
    // Z85 uses big endian encoded uint32
    uint32_t val = (uint32_t)chunk[0] << 24;
    val |= (uint32_t)chunk[1] << 16;
    val |= (uint16_t)chunk[2] << 8;
    val |= chunk[3];
    
    for (int8_t i = 4; i >= 0; i--) {
#ifdef TEST_NO_MCU
        z85_encoded[i] = z85_map[val % 85];
#else
        z85_encoded[i] =
            pgm_read_byte(&(z85_map[(uint8_t)(val % 85)]));
#endif
    val /= 85;
    }
}
