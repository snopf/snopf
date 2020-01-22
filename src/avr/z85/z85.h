// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#ifndef __z85_H__
#define __z85_H__

#include <stdint.h>

/*
 * Z85 Encoding optimized for the 8 bit avr with little ram usage.
 * Z85 includes all letters (lower and capital), all numbers and 23 special
 * characters from the ASCII alphabet. Special characters that are sometimes
 * wrongly evaluated by internet forms are omitted, e.g. quotation marks.
 */

// Z85 encode the sha256_hash chunk of 4 bytes length
void z85_encode_chunk(char z85_encoded[5], const uint8_t sha256_hash[4]);

#endif
